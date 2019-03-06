"""

Faraday depth spectra for a Faraday thick source 

Given an input file, the script removes user specified number of lines

The script generates a new file with a reduced number of entries

The scripts also creates a directory with the same name as files


Some rows of data have been deliberately removed to mimic RFI flagging

The algorithm picks a random number of blocks of lines, randomly

The generated files and the output images are stored in the new directory

"""


import os,sys

import random

from random import randint

from random import sample

import numpy as np

import pylab as pl

import rm_tools as R


#----------------------------------------------------------------

def trim_data(percent, name2, filename2, filename3, num2= 1024, filename1="./data/all_params.txt"):

       num1 = int(round((num2*percent/100), 0)) 

       with open(filename1) as file:

           lines = file.read().splitlines()

       #random_lines = random.sample(lines, num1) 
       n = randint(2,5)

       addends = []

       picks = range(1, num1)

       while sum(addends) != num1:

            addends = random.sample(picks, n-1)

            if sum(addends) > num1-1:

                continue

            addends.append(num1 - sum(addends))

       random_lines = []

       num_max = len(lines)-max(addends)

       for i in addends:
          
          random_line_num = random.randrange(0, num_max)

          count = 0

          while count < i:

              #random_line_num = random.randrange(0, len(lines)-max(addends)) 

              random_lines.append(lines[random_line_num])

              random_line_num+=1

              count +=1

          print "Random line number: {}".format(random_line_num) 

          i+=1  
     
       print "Random line number(max): {}".format(num_max)     



       with open(filename2, "w") as output_file1:  

            output_file1.writelines(line + '\n' for line in lines if line not in random_lines)

            output_file1.close()  

       with open(filename3, "w") as output_file2:  

            output_file2.writelines(line + '\n' for line in lines if line in random_lines)

            output_file2.close()


       num_of_lines = num2 - num1

       remainder = 100 - percent

       print n

       print addends

       #print random_lines

       return remainder


# -----------------------------------------------------------------



def get_1d_data(input_dir):



        files = os.listdir(input_dir)


        params_file = './' + name2 + '/' + "training" + '.txt'

        nu = np.loadtxt(params_file, usecols=(0,))

        lam_squared = np.loadtxt(params_file, usecols=(1,))

        stokesQ = np.loadtxt(params_file, usecols=(2,))

        stokesU = np.loadtxt(params_file, usecols=(3,)) 
        

        los = stokesQ + 1j*stokesU

        return nu,los


# -----------------------------------------------------------------



def calc_phi_res(nu):



        C2 = 8.98755179e16

        nus = np.sort(nu)

        delta_l2 = C2 * (nus[0] ** (-2) - nus[-1] ** (-2))



        res = 2. * np.sqrt(3) / delta_l2



        return res



# -----------------------------------------------------------------



def calc_maxscale(nu,dnu):



        C2 = 8.98755179e16

        nus = np.sort(nu)

        delta_l2 = C2 * (nus[0] ** (-2) - nus[-1] ** (-2))



        l2min = 0.5 * C2 * ((nus[-1] + dnu) ** (-2)

                        + (nus[-1] - dnu) ** (-2))



        maxscale = np.pi / l2min



        return maxscale



# -----------------------------------------------------------------
#Retrive data from the file


percent = input('Please enter the percentage of entries to remove: ')

name2 = input('Please enter the name of the directory for the output files: ')

os.makedirs(name2)

input_dir = './' + name2 + '/'

filename2 = './' + name2 + '/' + "training" + '.txt'

filename3 = './' + name2 + '/' + "removed" + '.txt'

print 'A file {} with {} percent of the original data has been successfully generated'.format(filename2, trim_data(percent, name2, filename2, filename3, num2= 1024, filename1="./data/all_params.txt"))

nu = np.loadtxt( filename2, usecols=(0,))

lam_squared = np.loadtxt( filename2, usecols=(1,))

stokesQ = np.loadtxt( filename2, usecols=(2,))

stokesU = np.loadtxt(filename2, usecols=(3,))

 
#--------------------------------------------------------------------------

pl.subplot(111)

pl.plot(lam_squared,stokesQ)

pl.plot(lam_squared,stokesU)

pl.xlabel('$\lambda^2 [m^2]$')  

pl.ylabel('stokes parameters ')

pl.legend(['stokesQ','stokesU'])

pl.savefig(input_dir +'plot1.png')

pl.show()

#------------------------------------------------------------------------
# specify the range of fd space:

phi = np.linspace(-1000,1000,4000)



# get the input data:

#inputdir = "./data"

nu,los = get_1d_data(input_dir)

dnu = nu[1]-nu[0]



# initialise the pyrmsynth class:

rms = R.RMSynth(nu,dnu,phi)



# calculate the resolution in fd space and the maximum recoverable scale:

res = calc_phi_res(nu)

maxscale = calc_maxscale(nu,dnu)

print "\n"

print "Max f.d. resolution: " +str(round(res)) + " rad/m^2"

print "Max f.d. scale " +str(round(maxscale)) + " rad/m^2"

print "\n"



# plot the RMTF:

pl.subplot(111)

pl.plot(rms.rmsf_phi,np.abs(rms.rmsf))

pl.axis([-1000,1000,-0.1,1.1])

pl.xlabel('RMSF ($\phi$)')   

pl.ylabel('RMSF')

pl.savefig(input_dir + 'plot2.png')

pl.show()



# run the RM synthesis transform on the data:

fd_spec = rms.compute_dirty_image(los)



# plot the output:

pl.subplot(111)
 
pl.plot(phi,np.abs(fd_spec))

pl.xlabel('$\phi$ [rad $m^{-2}$]')

pl.ylabel('F ($\phi$)')

pl.axis([-1000,1000,-0.1,1.5])

pl.savefig(input_dir +'plot3.png')

pl.show()
