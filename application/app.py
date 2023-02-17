from flask import Flask, render_template,request
from pylsl import StreamInlet, resolve_stream # first resolve an EEG # stream on the lab network
from scipy import signal
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/', methods = ['POST','GET'])






def calculate():
    """
        calculate() function do the cumputation where as per the chosen channel number of device by the user, the resultant graph 
        of Power Spactral Density vs Frequency gets displayed. It also calculates individual total band powers and their relative band powers.

            :parameter p1: No parameter.
            :return: 'index.html',
                            channel=[{'noc': 'Channel Number'}, {'noc': 0}, {'noc': 1}, {'noc': 2}, {'noc': 3}, {'noc': 4}],
                            url,
                             tot,
                            sum_delta,
                            sum_theta,
                            sum_alpha,
                            sum_beta,
                            delta_band_power,
                            theta_band_power,
                            alpha_band_power,
                            beta_band_power

    """

    url=''

    tot=0,
    sum_delta=0,
    sum_theta=0,
    sum_alpha=0,
    sum_beta=0,
    delta_band_power=0.0,
    theta_band_power=0.0,
    alpha_band_power=0.0,
    beta_band_power=0.0

    if request.method == 'POST' and 'channel' in request.form:
    
        print("looking for an EEG stream...")
        streams = resolve_stream('type', 'EEG') # create a new inlet to read # from the stream
        inlet = StreamInlet(streams[0])  
        
        ch=request.form.get('channel')
        if ch != 'Channel Number':
            ch=int(ch)
            url='/static/images/plot.png'

        print('selected channel: ',ch)
            
        i=0
        lst=[]
        
        while True:    
            
            if i==500:
                break
            else:
                sample, timestamp = inlet.pull_sample() 
                lst.append(sample)
                print(sample)
            i=i+1

        eeg_data_n=[item[ch] for item in lst]

        filePath = "myfile.txt"

        if os.path.exists(filePath):
            os.remove(filePath)
            print('Previous file removed and new file created')
            file1 = open(filePath,"a")
        else:
            #print('new file created')
            file1 = open(filePath,"a")

        for i in eeg_data_n:
            val=str(i)+'\n'
            file1.write((val))
            
        file1.close() 

        data = np.loadtxt('myfile.txt')
        # Define sampling frequency and time vector
        sf = 100
        time = np.arange(data.size) / sf

        # Define window length (4 seconds)
        win = 4 * sf
        freqs, psd = signal.welch(data, sf, nperseg=win)
    
        sns.set(font_scale=1.2, style='white')
        plt.figure(figsize=(20, 10))
        plt.plot(freqs, psd, color='k', lw=2)
        plt.xlabel('Frequency (Hz)', labelpad=20)
        #plt.vlines([1.5,4,8,14,30], 1.5,175000, linestyles='dashed', colors='red')
        plt.axvspan(1.5, 4, color='salmon', alpha=0.5)
        plt.axvspan(4,8, color='aquamarine', alpha=0.5)
        plt.axvspan(8,14, color='gold', alpha=0.5)
        plt.axvspan(14,30, color='cornflowerblue', alpha=0.5)
        #plt.vlines([12], 0, 1000, linestyles='dashed', colors='blue')
        plt.ylabel('Power spectral density (V^2 / Hz)',labelpad=20)
        plt.ylim([1.5, psd.max() * 1.1])
        plt.title(f"Selected Channel Number: %d" % ch, y=1.05)
        plt.xticks(np.arange(0, len(freqs)+1, 2))
        plt.xlim([1.5, 30])  #plt.xlim([0, freqs.max()])
        plt.legend(['Line: Freq vs Power', '1.5-4 (Delta)','4-8 (Theta)','8-14 (Alpha)','14-30 (Beta)'], 
                bbox_to_anchor=(1,1), loc= 'upper right')
        sns.despine()
    
        # fig_(fig)

        plt.savefig('static/images/plot.png')  
        
        ###To get total power of all ferq bands:
        tot=0
        for i in range(6,len(psd)):
            
            tot=tot+psd[i]
 
        #print(max(freqs),'  max freq', ' index of psd:',(len(psd)+1), ' total:',tot)

        if max(freqs)>=4:
            #For Delta graph
            lst=[]
            sns.set(font_scale=1.2, style='white')
            plt.figure(figsize=(20, 10))
            plt.plot(freqs, psd, color='k', lw=1,  marker='o')

            for x,y in zip(freqs,psd):

                label = "{:.2f}".format(y)

                plt.annotate(label, 
                    (x,y),
                    textcoords="offset points",
                    xytext=(0,10), 
                    
                    ha='center',
                    arrowprops=dict(arrowstyle="->", color='green'))

            plt.xlabel('Frequency (Hz)', labelpad=20)
            plt.axvspan(1.5, 4, color='salmon', alpha=0.5)
            plt.legend(['Line: Freq vs Power', '1.5-4 (Delta)'], 
            bbox_to_anchor=(1,1), loc= 'upper right')
            plt.xlim([1.5, 4])
            first=int((np.where(freqs == 1.5))[0])
            last=int((np.where(freqs == 4.0))[0])
            print(first,'1st ',last,' last')
            #to get the band power for delta range
            sum_delta=0

            for i in range(first,last+1):
                sum_delta=sum_delta+psd[i]
                #print(i, '', psd[i])
            delta_band_power=(sum_delta/tot)*100    
            print('sum_delta ',sum_delta,' sum_delta/tot= ',sum_delta/tot, ' ',delta_band_power)
           
            for i in range(first,last+1):
                lst.append(psd[i])
            #print(max(lst), '  max Delta')
            plt.ylim([1.5, max(lst)+5])  #plt.xlim([0, freqs.max()])
            plt.ylabel('Power spectral density (V^2 / Hz)', labelpad=20)

            plt.title(f"Total Delta Power: %s V^2 / Hz || Relative Delta power: %s %% " 
                % (str(sum_delta), str(delta_band_power)), y=1.05)
            sns.despine()
            plt.savefig('static/images/Delta.png')  
        
    #For Theta graph
        if max(freqs)>=8:
            
            lst=[]
            sns.set(font_scale=1.2, style='white')
            plt.figure(figsize=(20, 10))
            plt.plot(freqs, psd, color='k', lw=2)

            for x,y in zip(freqs,psd):

                label = "{:.3f}".format(y)

                plt.annotate(label, 
                    (x,y), 
                    textcoords="offset points",
                    xytext=(0,10), 
              
                    ha='center',
                    arrowprops=dict(arrowstyle="->", color='green'))

            plt.xlabel('Frequency (Hz)', labelpad=20)
            plt.axvspan(4,8, color='aquamarine', alpha=0.5)
            plt.legend(['Line: Freq vs Power', '4-8 (Theta)'],
            bbox_to_anchor=(1,1), loc= 'upper right')
            plt.xlim([4,8])
            first=int((np.where(freqs == 4.0))[0])
            last=int((np.where(freqs == 8.0))[0])
            
            #to get the band power for Theta range
            sum_theta=0

            for i in range(first+1,last+1):
                sum_theta = sum_theta + psd[i]
                #print(i, '', psd[i])
            theta_band_power= (sum_theta/tot)*100      
            print('sum_theta ',sum_theta,' sum_theta/tot= ',sum_theta/tot, ' ',theta_band_power)
           
            for i in range(first,last+1):
                lst.append(psd[i])
            #print(max(lst), '  max Theta')
            plt.ylim([1.5, max(lst)+5]) #plt.xlim([0, freqs.max()])
            plt.ylabel('Power spectral density (V^2 / Hz)')
            plt.title(f"Total Theta Power: %s V^2 / Hz || Relative Theta power: %s %%" 
                % (str(sum_theta), str(theta_band_power)), y=1.05)

            sns.despine()
            plt.savefig('static/images/Theta.png')  

    #For Alpha graph
        if max(freqs)>=14:
            #For Alpha graph
            lst=[]
            sns.set(font_scale=1.2, style='white')
            plt.figure(figsize=(20, 10))
            plt.plot(freqs, psd, color='k', lw=2)

            for x,y in zip(freqs,psd):

                label = "{:.3f}".format(y)

                plt.annotate(label, 
                    (x,y), 
                    textcoords="offset points",
                    xytext=(0,10),
                    # and the text label
                    ha='center',
                    arrowprops=dict(arrowstyle="->", color='green'))

            plt.xlabel('Frequency (Hz)', labelpad=20)
            plt.axvspan(8,14, color='gold', alpha=0.5)
            plt.legend(['Line: Freq vs Power', '8-14 (Alpha)'], 
            bbox_to_anchor=(1,1), loc= 'upper right')
            plt.xlim([8,14])
            first=int((np.where(freqs == 8.0))[0])
            last=int((np.where(freqs == 14.0))[0])
            
            #to get the band power for Alpha range
            sum_alpha=0

            for i in range(first+1,last+1):
                sum_alpha = sum_alpha + psd[i]
                #print(i, '', psd[i])
            alpha_band_power = (sum_alpha/tot )*100     
            print('sum_alpha ',sum_alpha,' sum_alpha/tot= ',sum_alpha/tot, ' ',alpha_band_power)
         
            
            #to set Y limit as per highest value of Y in X- range
            for i in range(first,last+1):
                lst.append(psd[i])
            #print(max(lst), '  max aplha')
            plt.ylim([1.5, max(lst)+5])
            plt.ylabel('Power spectral density (V^2 / Hz)', labelpad=20)
            plt.title(f"Total Alpha Power: %s V^2 / Hz || Relative Alpha power: %s %%" 
                % (str(sum_alpha), str(alpha_band_power)), y=1.05)
            
            sns.despine()
            plt.savefig('static/images/Alpha.png')  

    #For Beta graph
        if max(freqs)<=30 and max(freqs)>14:
            #For Beta graph
            lst=[]
            sns.set(font_scale=1.2, style='white')
            plt.figure(figsize=(20, 10))
            plt.plot(freqs, psd, color='k', lw=2)

            for x,y in zip(freqs,psd):

                label = "{:.2f}".format(y)

                plt.annotate(label, 
                    (x,y), 
                    textcoords="offset points",
                    xytext=(0,10), 
                   
                    ha='center',
                    arrowprops=dict(arrowstyle="->", color='green'))

            plt.xlabel('Frequency (Hz)', labelpad=20)
            plt.axvspan(14,30, color='cornflowerblue', alpha=0.5)
            plt.legend(['Line: Freq vs Power', '14-30 (Beta)'], 
            bbox_to_anchor=(1,1), loc= 'upper right')
            plt.xlim([14,30])
            first=int((np.where(freqs == 14.0))[0])
            last=int((np.where(freqs == max(freqs)))[0])
            
            sum_beta=0

            for i in range(first+1,last+1):
                sum_beta = sum_beta + psd[i]
                #print(i, '', psd[i])
            beta_band_power = (sum_beta/tot)*100      
            #print('sum_beta ',sum_beta,' sum_beta/tot= ',sum_beta/tot, ' ',beta_band_power)
      

            #to set Y limit as per highest value of Y in X- range
            for i in range(first,last+1):
                lst.append(psd[i])
            #print(max(lst), '  max aplha')
            plt.ylim([1.5, max(lst)+5])
            plt.ylabel('Power spectral density (V^2 / Hz)', labelpad=20)
            plt.title(f"Total Beta Power: %s V^2 / Hz || Relative Beta power: %s %%" 
                % (str(sum_beta), str(beta_band_power)), y=1.05)
            
            sns.despine()
            plt.savefig('static/images/Beta.png') 

        elif max(freqs)>30:
            #For Beta graph
            lst=[]
            sns.set(font_scale=1.2, style='white')
            plt.figure(figsize=(20, 10))
            plt.plot(freqs, psd, color='k', lw=2)


            for x,y in zip(freqs,psd):

                label = "{:.3f}".format(y)

                plt.annotate(label, # this is the value which we want to label (text)
                    (x,y), # x and y is the points location where we have to label
                    textcoords="offset points",
                    xytext=(0,10), # this for the distance between the points
                    # and the text label
                    ha='center',
                    arrowprops=dict(arrowstyle="->", color='green'))
                    
            plt.xlabel('Frequency (Hz)', labelpad=20)
            plt.axvspan(14,30, color='cornflowerblue', alpha=0.5)
            plt.legend(['Line: Freq vs Power', '14-30 (Beta)'], 
            bbox_to_anchor=(1,1), loc= 'upper right')
            plt.xlim([14,30])
            first=int((np.where(freqs == 14.0))[0])
            last=int((np.where(freqs == 30.0))[0])
            
            sum_beta=0

            for i in range(first+1,last+1):
                sum_beta=sum_beta+psd[i]
                #print(i, '', psd[i])
            beta_band_power=(sum_beta/tot)*100      
            #print('sum_beta ',sum_beta,' sum_beta/tot= ',sum_beta/tot, ' ',beta_band_power)
            

            #to set Y limit as per highest value of Y in X- range
            for i in range(first,last+1):
                lst.append(psd[i])
            #print(max(lst), '  max Beta')
            plt.ylim([1.5, max(lst)+5])
            plt.ylabel('Power spectral density (V^2 / Hz)', labelpad=20)
            plt.title(f"Total Beta Power: %s V^2 / Hz || Relative Beta power: %s %%" % (str(sum_beta), str(beta_band_power)), y=1.05)
            
            plt.savefig('static/images/Beta.png') 

    #    
        print(freqs)
        print(psd)
        print(max(freqs),'  max freq', ' index of psd:',(len(psd)+1), ' total:',tot)
       
    return render_template('index.html',
                            channel=[{'noc': 'Channel Number'}, {'noc': 0}, {'noc': 1}, {'noc': 2}, {'noc': 3}, {'noc': 4}],
                            url=url,
                             tot=tot,
                            sum_delta=sum_delta,
                            sum_theta=sum_theta,
                            sum_alpha=sum_alpha,
                            sum_beta=sum_beta,
                            delta_band_power=delta_band_power,
                            theta_band_power=theta_band_power,
                            alpha_band_power=alpha_band_power,
                            beta_band_power=beta_band_power)
   

   

# New functions
@app.route("/about/")

def about():

    """
        about() function shows the about page where a brief discription of the application is mentioned.

            :parameter p1: No parameter.
            :return: "about.html",url

    """

    return render_template("about.html",url='/static/images/muse_pic.png')



@app.route("/participant_page/", methods = ['POST','GET'])

def participant_page():
 
    """
        participant_page() function computes .

            :parameter p1: No parameter.
            :return: "participant_page.html", band, url

    """


    url_=''
    if request.method == 'POST' and 'band' in request.form:
        
        band=request.form.get('band')
        print('selected Frequency band: ',band)
        if band ==  'Delta: 0-4 Hz':
            url_='/static/images/Delta.png'
        if band ==  'Theta: 4-8 Hz':
            url_='/static/images/Theta.png'
        if band ==  'Alpha: 8-14 Hz':
            url_='/static/images/Alpha.png'
        if band ==  'Beta: 14-30 Hz':
            url_='/static/images/Beta.png'
    
    return render_template('participant_page.html',
                            band=[{'band': 'Select Band Name'}, {'band': 'Delta: 0-4 Hz'}, {'band': 'Theta: 4-8 Hz'}, {'band': 'Alpha: 8-14 Hz'}, {'band': 'Beta: 14-30 Hz'}],
                            url_=url_
                           )
   
