from PyQt5.QtWidgets import *
import sys,pickle

from PyQt5 import uic, QtWidgets ,QtCore, QtGui
from sklearn.preprocessing import LabelEncoder

import model,table_display,data_visualise,exi
import mlp,pre_trained,add_steps
####
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from keras.callbacks import ModelCheckpoint, TensorBoard

from keras.models import Sequential
from keras.layers import Dense

import seaborn as sns

import numpy as np

"""# Set Randomization Seed"""

SEED = 123

from numpy.random import seed
seed(SEED)
import tensorflow
tensorflow.random.set_seed(SEED)

df = pd.read_csv('D:/2023-student-project/karthick/Update_code/coo/creditcard.csv')

df.sample(n = 10)

"""# Plot the labels distribution"""

labels_dist = pd.value_counts(df['Class'], sort = True)

labels_dist.plot(kind = 'bar', rot = 0)
plt.title('Transaction Class Distribution')
plt.xticks(range(2), ["Normal", "Fraud"])
plt.xlabel('Class')
plt.ylabel('Frequency')


print(labels_dist)

"""# Plot transactions amount"""

frauds = df[df.Class == 1]
normal = df[df.Class == 0]


print(frauds['Amount'].describe()) #frauds.Amount.describe()
print('\n')
print(normal['Amount'].describe())

wholeFrame, (subFrame1, subFrame2) = plt.subplots(2, 1, sharex = True)

wholeFrame.suptitle('Amount per transaction by class')

BIN = 50

subFrame1.hist(frauds['Amount'], bins = BIN)
subFrame2.hist(normal['Amount'], bins = BIN)

subFrame1.set_title('Fraud')
subFrame2.set_title('Normal')

plt.xlabel('Amount ($)')
plt.ylabel('Number of Transactions')

plt.xlim(0, 20000)
plt.yscale('log')

plt.scatter(frauds['Time'], frauds['Amount'])
plt.xlabel('Time')
plt.ylabel('Amount')
plt.title('Time vs Amount')

#No visibly patterns of difference of amount transactions with time changes

"""# Remove unecessary descriptors / features"""

df.drop(["Time"], axis = 1, inplace = True)

df.head(n = 5)

"""# Check for Null and remove duplicates """

df.drop_duplicates(inplace = True)

if  df.isnull().values.any() != False:
        df.fillna(0)

"""# Standardize to 0 mean and 1.0 variance for Amount column"""

df['Amount'] = StandardScaler().fit_transform(df['Amount'].values.reshape(-1, 1))

"""# Split Data to Training and Testing Data"""

SPLIT = 0.2
training_data, testing_data = train_test_split(df, test_size = SPLIT, random_state = SEED)

training_data = training_data[training_data.Class == 0]
training_data = training_data.drop(['Class'], axis=1)

testing_labels = testing_data['Class']
testing_data = testing_data.drop(['Class'], axis=1)

# change to numpy array
training_data = training_data.values
testing_data = testing_data.values

print(training_data.shape)

"""# Build Autoencoder"""

feature_dim = 32

autoencoder = Sequential()
autoencoder.add(Dense(units = feature_dim, input_shape = (training_data.shape[1], ), activation = "relu"))#, activity_regularizer=regularizers.l1(10e-5)))
autoencoder.add(Dense(units = int(feature_dim / 2), activation = "relu"))

autoencoder.add(Dense(units = int(feature_dim / 4), activation = "relu"))
autoencoder.add(Dense(units = int(feature_dim / 4), activation = "relu"))

autoencoder.add(Dense(units = int(feature_dim / 2), activation = "relu"))
autoencoder.add(Dense(units = feature_dim, activation = "relu"))
autoencoder.add(Dense(units = training_data.shape[1], activation = 'linear'))

autoencoder.compile(optimizer='adam', 
                    loss='mean_squared_error', 
                    metrics=['accuracy'])

autoencoder.summary()


EPOCH = 100
BATCH_SIZE = 128

checkpointer = ModelCheckpoint(filepath="model.h5",
                               verbose = 0,
                               save_best_only=True)

tensorboard = TensorBoard(log_dir='./logs',
                          histogram_freq=0,
                          write_graph=True,
                          write_images=True)

history = autoencoder.fit(training_data, training_data, 
                          epochs = EPOCH, 
                          batch_size = BATCH_SIZE,
                          shuffle = True,
                          validation_data = (testing_data, testing_data),
                          verbose = 0,
                          callbacks=[checkpointer, tensorboard]).history

plt.plot(history['loss'])
plt.plot(history['val_loss'])

plt.title('Training Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend(['Train', 'Test'], loc = 'upper right')

predictions = autoencoder.predict(testing_data)
mse = np.mean(np.power(predictions - testing_data, 2), axis=1)
error_df = pd.DataFrame({'reconstruction_error': mse,
                        'true_class': testing_labels})
error_df.describe()

"""# Reconstruction Error Without Fraud"""

fig = plt.figure()
ax = fig.add_subplot(111)
normal_error_df = error_df[(error_df['true_class']== 0) & (error_df['reconstruction_error'] < 10)]
_ = ax.hist(normal_error_df.reconstruction_error.values, bins=10)

"""# Reconstruction Error With Fraud"""

fig = plt.figure()
ax = fig.add_subplot(111)
fraud_error_df = error_df[error_df['true_class'] == 1]
_ = ax.hist(fraud_error_df.reconstruction_error.values, bins=10)

from sklearn.metrics import (confusion_matrix, precision_recall_curve, auc,
                             roc_curve, recall_score, classification_report, f1_score,
                             precision_recall_fscore_support)

fpr, tpr, thresholds = roc_curve(error_df.true_class, error_df.reconstruction_error)
roc_auc = auc(fpr, tpr)

plt.title('Receiver Operating Characteristic')
plt.plot(fpr, tpr, label='AUC = %0.4f'% roc_auc)
plt.legend(loc='lower right')
plt.plot([0,1],[0,1],'r--')
plt.xlim([-0.001, 1])
plt.ylim([0, 1.001])
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.show();

"""# Plot the testing data distribution"""

####################

class error_window(QMainWindow):
    def __init__(self):
        super(error_window, self).__init__()
        #uic.loadUi("../ui_files/error.ui", self)
        #self.show()



class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi("../ui_files/Mainwindow.ui", self)
 
        # find the widgets in the xml file
 
        #self.textedit = self.findChild(QTextEdit, "textEdit")
        #self.button = self.findChild(QPushButton, "pushButton")
        #self.button.clicked.connect(self.clickedBtn)
        global data,steps
        data=data_visualise.data_()
        steps=add_steps.add_steps()


        self.Browse = self.findChild(QPushButton,"Browse")
        self.Drop_btn = self.findChild(QPushButton,"Drop")
        
        self.fillna_btn = self.findChild(QPushButton,"fill_na")
        self.con_btn = self.findChild(QPushButton,"convert_btn")
        self.columns= self.findChild(QListWidget,"column_list")
        self.emptycolumn=self.findChild(QComboBox,"empty_column")
        self.cat_column=self.findChild(QComboBox,"cat_column")
        self.table = self.findChild(QTableView,"tableView")
        self.dropcolumns=self.findChild(QComboBox,"dropcolumn")
        self.data_shape = self.findChild(QLabel,"shape")
        self.fillmean_btn = self.findChild(QPushButton,"fillmean")
        self.submit_btn = self.findChild(QPushButton,"Submit")
        self.target_col =self.findChild(QLabel,"target_col")
        self.model_select=self.findChild(QComboBox,"model_select")
        #self.describe=self.findChild(QPlainTextEdit,"describe")
        #self.describe= self.findChild(QTextEdit,"Describe")
        
        self.scatter_x=self.findChild(QComboBox,"scatter_x")
        self.scatter_y=self.findChild(QComboBox,"scatter_y")
        self.scatter_mark=self.findChild(QComboBox,"scatter_mark")
        self.scatter_c=self.findChild(QComboBox,"scatter_c")
        self.scatter_btn = self.findChild(QPushButton,"scatterplot")
        
        self.plot_x=self.findChild(QComboBox,"plot_x")
        self.plot_y=self.findChild(QComboBox,"plot_y")
        self.plot_mark=self.findChild(QComboBox,"plot_marker")
        self.plot_c=self.findChild(QComboBox,"plot_c")
        self.plot_btn = self.findChild(QPushButton,"lineplot")

        self.hist_column=self.findChild(QComboBox,"hist_column")
        self.hist_column_add=self.findChild(QComboBox,"hist_column_add")
        self.hist_add_btn = self.findChild(QPushButton,"hist_add_btn")
        self.hist_remove_btn = self.findChild(QPushButton,"hist_remove_btn")
        self.histogram_btn = self.findChild(QPushButton,"histogram")

        self.heatmap_btn = self.findChild(QPushButton,"heatmap")

        self.columns.clicked.connect(self.target)
        self.Browse.clicked.connect(self.getCSV)
        self.Drop_btn.clicked.connect(self.dropc)
        self.scatter_btn.clicked.connect(self.scatter_plot)
        self.plot_btn.clicked.connect(self.line_plot)
        
        self.fillna_btn.clicked.connect(self.fillna)
        self.fillmean_btn.clicked.connect(self.fillme)
        
        self.hist_add_btn.clicked.connect(self.hist_add_column)
        self.hist_remove_btn.clicked.connect(self.hist_remove_column)
        self.histogram_btn.clicked.connect(self.histogram_plot)

        self.heatmap_btn.clicked.connect(self.heatmap_gen)

        self.con_btn.clicked.connect(self.con_cat)
        self.submit_btn.clicked.connect(self.set_target)

        self.train=self.findChild(QPushButton,"train")
        self.train.clicked.connect(self.train_func)
        self.scale_btn.clicked.connect(self.scale_value)
        
        self.pre_trained.clicked.connect(self.upload_model)
        self.go_pre_trained.clicked.connect(self.test_pretrained)
        self.show()

    def scale_value(self):

        #my_dict={"StandardScaler":standard_scale ,"MinMaxScaler":min_max, "PowerScaler":power_scale}
        if self.scaler.currentText()=='StandardScale':
            self.df,func_name = data.StandardScale(self.df,self.target_value)
        elif self.scaler.currentText()=='MinMaxScale':
            self.df,func_name = data.MinMaxScale(self.df,self.target_value)
        elif self.scaler.currentText()=='PowerScale':
            self.df,func_name = data.PowerScale(self.df,self.target_value)
        
        steps.add_text(self.scaler.currentText()+" applied to data")
        steps.add_pipeline(self.scaler.currentText(),func_name)
        self.filldetails()


    def hist_add_column(self):

        self.hist_column_add.addItem(self.hist_column.currentText())
        self.hist_column.removeItem(self.hist_column.findText(self.hist_column.currentText()))


    def hist_remove_column(self):
        
        self.hist_column.addItem(self.hist_column_add.currentText())
        self.hist_column_add.removeItem(self.hist_column_add.findText(self.hist_column_add.currentText()))


    def histogram_plot(self):
        
        AllItems = [self.hist_column_add.itemText(i) for i in range(self.hist_column_add.count())]
        for i in AllItems:
            data.plot_histogram(self.df,i)
        
        
    def heatmap_gen(self):

        data.plot_heatmap(self.df)

    def set_target(self):

        self.target_value=str(self.item.text()).split()[0]
        steps.add_code("target=data['"+self.target_value+"']")
        self.target_col.setText(self.target_value)

    def filldetails(self,flag=1):
         
        if(flag==0):  
            
            self.df = data.read_file(str(self.filePath))
        
        
        self.columns.clear()
        self.column_list=data.get_column_list(self.df)
        self.empty_list=data.get_empty_list(self.df)
        self.cat_col_list=data.get_cat(self.df)
        for i ,j in enumerate(self.column_list):
            stri=j+ " -------   " + str(self.df[j].dtype)
            self.columns.insertItem(i,stri)
            

        self.fill_combo_box() 
        shape_df="Shape:  Rows:"+ str(data.get_shape(self.df)[0])+"  Columns: "+str(data.get_shape(self.df)[1])
        self.data_shape.setText(shape_df)

    def fill_combo_box(self):
        
        self.dropcolumns.clear()
        self.dropcolumns.addItems(self.column_list)
        self.emptycolumn.clear()
        self.emptycolumn.addItems(self.empty_list)
        self.cat_column.clear()
        self.cat_column.addItems(self.cat_col_list)
        self.scatter_x.clear()
        self.scatter_x.addItems(self.column_list)
        self.scatter_y.clear()
        self.scatter_y.addItems(self.column_list)
        self.plot_x.clear()
        self.plot_x.addItems(self.column_list)
        self.plot_y.clear()
        self.plot_y.addItems(self.column_list)
        self.hist_column.clear()
        self.hist_column.addItems(data.get_numeric(self.df))
        self.hist_column.addItem("All")

        
        #self.describe.setText(data.get_describe(self.df))
        
        x=table_display.DataFrameModel(self.df)
        self.table.setModel(x)
        
    def upload_model(self):
        self.filePath_pre, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home/akshay/Dekstop',"pkl(*.pkl)")
        with open(self.filePath_pre, 'rb') as file:
            self.pickle_model = pickle.load(file)
        
    def test_pretrained(self):

        self.testing=pre_trained.UI(self.df,self.target_value,self.pickle_model,self.filePath_pre)

    def con_cat(self):
        
        a=self.cat_column.currentText()
        self.df[a],func_name =data.convert_category(self.df,a)
        steps.add_text("Column "+ a + " converted using LabelEncoder")
        steps.add_pipeline("LabelEncoder",func_name)
        self.filldetails()

    def fillna(self):

        self.df[self.emptycolumn.currentText()]=data.fillna(self.df,self.emptycolumn.currentText())
        code="data['"+self.emptycolumn.currentText()+"'].fillna('"'Uknown'"',inplace=True)"
        steps.add_code(code)
        steps.add_text("Empty values of "+ self.emptycolumn.currentText() + " filled with Uknown")
        self.filldetails()

    def fillme(self):

        self.df[self.emptycolumn.currentText()]=data.fillmean(self.df,self.emptycolumn.currentText())
        code="data['"+column+"'].fillna(data['"+self.emptycolumn.currentText()+"'].mean(),inplace=True)"
        steps.add_code(code)
        steps.add_text("Empty values of "+ self.emptycolumn.currentText() + " filled with mean value")
        self.filldetails()

    def getCSV(self):
        self.filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '/home/akshay/Downloads/ML Github/datasets',"csv(*.csv)")
        self.columns.clear()
        code="data=pd.read_csv('"+str(self.filePath)+"')"
        steps.add_code(code)
        steps.add_text("File "+self.filePath+" read")
        if(self.filePath!=""):
            self.filldetails(0)


    def target(self):
        self.item=self.columns.currentItem()
        
     
 
    def dropc(self):

        if (self.dropcolumns.currentText() == self.target_value):
            self.target_value=""
            self.target_col.setText("")
        self.df=data.drop_columns(self.df,self.dropcolumns.currentText())
        steps.add_code("data=data.drop('"+self.dropcolumns.currentText()+"',axis=1)")
        steps.add_text("Column "+ self.dropcolumns.currentText()+ " dropped")
        self.filldetails()  

    def scatter_plot(self):

        data.scatter_plot(df=self.df,x=self.scatter_x.currentText(),y=self.scatter_y.currentText(),c=self.scatter_c.currentText(),marker=self.scatter_mark.currentText())

        

    def line_plot(self):

        data.line_plot(df=self.df,x=self.plot_x.currentText(),y=self.plot_y.currentText(),c=self.plot_c.currentText(),marker=self.plot_mark.currentText())
     
    def train_func(self):

        myDict={ "LSTM":model, "CLSTM":exi}
        
        if(self.target_value!=""):
            
            self.win = myDict[self.model_select.currentText()].UI(self.df,self.target_value,steps)
            
                    
        

app = QApplication(sys.argv)
window = UI()
error_w=error_window()
app.exec_()

###############################################

labels_dist = pd.value_counts(testing_labels, sort = True)

labels_dist.plot(kind = 'bar', rot = 0)
plt.title('Transaction Class Distribution')
plt.xticks(range(2), ["Normal", "Fraud"])
plt.xlabel('Class')
plt.ylabel('Frequency')

labels_dist

threshold = 0.7

pred_y = [1 if e > threshold else 0 for e in error_df.reconstruction_error.values]

conf_matrix = confusion_matrix(error_df.true_class, pred_y)

[tn, fp], [fn, tp] = conf_matrix

#reminder: tp is fraud
plt.figure(figsize=(6, 6))

sns.heatmap(conf_matrix, xticklabels=["Normal", "Fraud"], yticklabels=["Normal", "Fraud"], annot=True, fmt="d");
plt.title("Confusion matrix")
plt.ylabel('True class')
plt.xlabel('Predicted class')
plt.show()   

print(labels_dist)

groups = error_df.groupby('true_class')
fig, ax = plt.subplots()

for name, group in groups:
    ax.plot(group.index, group.reconstruction_error, marker='o', ms=3.5, linestyle='',
            label= "Fraud" if name == 1 else "Normal")
ax.hlines(threshold, ax.get_xlim()[0], ax.get_xlim()[1], colors="r", zorder=100, label='Threshold')
ax.legend()
plt.title("Reconstruction error for different classes")
plt.ylabel("Reconstruction error")
plt.xlabel("Data point index")
plt.show();

precision, recall, th = precision_recall_curve(error_df.true_class, error_df.reconstruction_error)
plt.plot(recall, precision, 'b', label='Precision-Recall curve')
plt.title('Recall vs Precision')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.show()
print(th)

plt.plot(th, precision[1:], 'b', label='Threshold-Precision curve')
plt.title('Precision for different threshold values')
plt.xlabel('Threshold')
plt.ylabel('Precision')
plt.xlim(0, 50)
plt.show()
#activity_regularizer how to set value, how does value affect

plt.plot(th, recall[1:], 'b', label='Threshold-Recall curve')
plt.title('Recall for different threshold values')
plt.xlabel('Reconstruction error')
plt.ylabel('Recall')
plt.xlim(0, 50)
plt.show()
#################################################3