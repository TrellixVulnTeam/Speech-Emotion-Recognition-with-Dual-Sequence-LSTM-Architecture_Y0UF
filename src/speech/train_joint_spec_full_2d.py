import torch
from torch import optim
from model_joint_spec_full_2d import SpectrogramModel
from process_joint_spec_full_2d import IEMOCAP,my_collate
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import ReduceLROnPlateau, CosineAnnealingLR, MultiStepLR
import pdb
from torch.nn import DataParallel
import pickle
import numpy as np
from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence
import argparse
def init_parser():
    parser = argparse.ArgumentParser(description='Train and test your model as specified by the parameters you enter')
    parser.add_argument('--name', '-n', default='mel', type=str, dest='name')
    parser.add_argument('--nfft','-fft',default=512,type=int,dest='nfft')
    parser.add_argument('--batch_size', '-b', default=128, type=int, dest='batch_size')
    parser.add_argument('--out_channels_1', '-out1', default=64, type=int, dest='out_channels1')
    parser.add_argument('--out_channels_2', '-out2', default=16, type=int, dest='out_channels2')
    parser.add_argument('--kernel_size_cnn_1', '-kc1', default=2, type=int, dest='kernel_size_cnn1')
    parser.add_argument('--kernel_size_cnn_2','-kc2',default=2,type=int,dest='kernel_size_cnn2')
    parser.add_argument('--stride_size_cnn_1', '-sc1', default=1, type=int, dest='stride_size_cnn1')
    parser.add_argument('--stride_size_cnn_2', '-sc2', default=1, type=int, dest='stride_size_cnn2')
    parser.add_argument('--kernel_size_pool_1', '-kp1', default=2, type=int, dest='kernel_size_pool1')
    parser.add_argument('--kernel_size_pool_2','-kp2',default=2,type=int,dest='kernel_size_pool2')
    parser.add_argument('--stride_size_pool', '-sp', default=2, type=int, dest='stride_size_pool')
    return parser.parse_args()
def train_model(args):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    device_ids=[0,1,2,3]
    batch_size=args.batch_size
    input_channels=1
    out_channels = [args.out_channels1,args.out_channels2]
    kernel_size_cnn = [[args.kernel_size_cnn1,args.kernel_size_cnn2]]*2
    stride_size_cnn = [[args.stride_size_cnn1,args.stride_size_cnn2]]*2
    kernel_size_pool = [[args.kernel_size_pool1,args.kernel_size_pool2]]*2
    stride_size_pool = [args.stride_size_pool]*2
    hidden_dim=200
    num_layers=2
    dropout=0
    num_labels=4
    hidden_dim_lstm=200
    epoch_num=40
    num_layers_lstm=2
    model = SpectrogramModel(input_channels,out_channels, kernel_size_cnn, stride_size_cnn, kernel_size_pool,
                                stride_size_pool, hidden_dim,num_layers,dropout,num_labels, batch_size,
                                hidden_dim_lstm,num_layers_lstm,device,args.nfft,False)
    '''
    print("============================ Number of parameters ====================================")
    print(str(sum(p.numel() for p in model.parameters() if p.requires_grad)))
    '''
    
    path="name:{};nfft:{};batch_size:{};out_channels:{};kernel_size_cnn:{};stride_size_cnn:{};kernel_size_pool:{};stride_size_pool:{}".format(args.name,args.nfft,args.batch_size,out_channels,kernel_size_cnn,stride_size_cnn,kernel_size_pool,stride_size_pool)
    with open("/scratch/speech/models/classification/spec_full_joint_stats_2.txt","a+") as f:
        f.write("\n"+"============ model starts ===========")
        f.write("\n"+"model_parameters: "+str(sum(p.numel() for p in model.parameters() if p.requires_grad))+"\n"+path+"\n")
    model.cuda()
    model=DataParallel(model,device_ids=device_ids)
    model.train()

    # Use Adam as the optimizer with learning rate 0.01 to make it fast for testing purposes
    optimizer = optim.Adam(model.parameters(),lr=0.001)
    optimizer2=optim.SGD(model.parameters(), lr=0.1)
    scheduler = ReduceLROnPlateau(optimizer=optimizer,factor=0.5, patience=2, threshold=1e-3)
    #scheduler2=ReduceLROnPlateau(optimizer=optimizer2, factor=0.5, patience=2, threshold=1e-3)
    #scheduler2 =CosineAnnealingLR(optimizer2, T_max=300, eta_min=0.0001)
    scheduler3 =MultiStepLR(optimizer, [5,10,15],gamma=0.1)

    # Load the training data
    training_data = IEMOCAP(name=args.name, nfft=args.nfft, train=True)
    train_loader = DataLoader(dataset=training_data, batch_size=batch_size, shuffle=True, collate_fn=my_collate, num_workers=0, drop_last=True)
    testing_data = IEMOCAP(name=args.name, nfft=args.nfft, train=False)
    test_loader = DataLoader(dataset=testing_data, batch_size=batch_size, shuffle=True, collate_fn=my_collate, num_workers=0,drop_last=True)
    #print("=================")
    #print(len(training_data))
    #print("===================")
    test_acc=[]
    train_acc=[]
    test_loss=[]
    train_loss=[]
    for epoch in range(epoch_num):  # again, normally you would NOT do 300 epochs, it is toy data
        #print("===================================" + str(epoch+1) + "==============================================")
        losses = 0
        correct=0
        model.train()
        for j, (input_lstm,input, target,seq_length,seq_length_spec) in enumerate(train_loader):
            #if (j+1)%20==0: print("=================================Train Batch"+ str(j+1)+str(weight)+"===================================================")
            model.zero_grad()
            #input_lstm = pad_sequence(sequences=input_lstm,batch_first=True)
            losses_batch,correct_batch= model(input_lstm,input, target,seq_length,seq_length_spec)
            loss = torch.mean(losses_batch,dim=0)
            correct_batch=torch.sum(correct_batch,dim=0)
            losses += loss.item() * batch_size
            loss.backward()
            weight=model.module.state_dict()["weight"]
            weight=torch.exp(10*weight)/(1+torch.exp(10*weight)).item()
            optimizer.step()
            correct += correct_batch.item()
        accuracy=correct*1.0/((j+1)*batch_size)
        losses=losses / ((j+1)*batch_size)
        #scheduler3.step()
        losses_test = 0
        correct_test = 0
        #torch.save(model.module.state_dict(), "/scratch/speech/models/classification/spec_full_joint_checkpoint_epoch_{}.pt".format(epoch+1))
        model.eval()
        with torch.no_grad():
            for j,(input_lstm,input, target,seq_length,seq_length_spec) in enumerate(test_loader):
                #if (j+1)%10==0: print("=================================Test Batch"+ str(j+1)+ "===================================================")
                #input_lstm = pad_sequence(sequences=input_lstm,batch_first=True)
                losses_batch,correct_batch= model(input_lstm,input, target,seq_length,seq_length_spec)
                loss = torch.mean(losses_batch,dim=0)
                correct_batch=torch.sum(correct_batch,dim=0)
                losses_test += loss.item() * batch_size
                correct_test += correct_batch.item()

        #print("how many correct:", correct_test)
        accuracy_test = correct_test * 1.0 / ((j+1)*batch_size)
        losses_test = losses_test / ((j+1)*batch_size)

        # data gathering
        test_acc.append(accuracy_test)
        train_acc.append(accuracy)
        test_loss.append(losses_test)
        train_loss.append(losses)
        #print("Epoch: {}-----------Training Loss: {} -------- Testing Loss: {} -------- Training Acc: {} -------- Testing Acc: {}".format(epoch+1,losses,losses_test, accuracy, accuracy_test)+"\n")
        with open("/scratch/speech/models/classification/spec_full_joint_stats_2.txt","a+") as f:
            f.write("Epoch: {}-----------Training Loss: {} -------- Testing Loss: {} -------- Training Acc: {} -------- Testing Acc: {}".format(epoch+1,losses,losses_test, accuracy, accuracy_test)+"\n")
            if epoch==epoch_num-1: f.write("Best Accuracy:{}".format(max(test_acc))+"\n")
            if epoch==epoch_num-1: f.write("=============== model ends ==================="+"\n")





    pickle_out=open("/scratch/speech/models/classification/joint_spec_full_checkpoint_stats_"+path+".pkl","wb")
    pickle.dump({"test_acc":test_acc, "train_acc": train_acc, "train_loss": train_loss,"test_loss":test_loss},pickle_out)
    pickle_out.close()
    print("success:{}, Best Accuracy:{}".format(path,max(test_acc)))
if __name__ == '__main__':
    args = init_parser()
    train_model(args)

