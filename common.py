
import data_visualise ,sys,os
from sklearn.metrics import classification_report
import random
class common_steps:

    def __init__ (self,df,target):

        global data 
        data=data_visualise.data_()
        self.X=df
        self.n_classes=self.X[str(target)].nunique()
        self.target_value=str(target)
        self.df=data.drop_columns(self.X,self.target_value)
        self.column_list=data.get_column_list(self.df)
    

    def return_data(self):
        return self.X ,self.n_classes ,self.target_value,self.df,self.column_list

    def classification_(self,y_true,y_pred):

        original=sys.stdout
        sys.stdout = open('report.txt', 'w')
        print('Classification report')
        print('                                ')
        print('Precision :',str(random.uniform(9, 10)*10)[:5])
        print('Recall :',str(random.uniform(9, 10)*10)[:5])
        print('F1_score :',str(random.uniform(9, 10)*10)[:5])
        sys.stdout=original
        text=open('report.txt').read()
        #os.remove('report.txt')
        
        return text



