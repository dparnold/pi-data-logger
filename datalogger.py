import matplotlib as mpl
from numpy import average
mpl.use('Agg')		# Needed for creating graphs without a GUI
import os    		# For checking whether files exist and executing system commands 
import Adafruit_DHT # Library for the DHT22
import numpy as np  # For calculations ; always useful
import matplotlib.pyplot as plt # Matplotlib creates the graphs
import time			# Gives you the date and time stamps

sensor = Adafruit_DHT.DHT22
pin = 4	# Pin 4 on Raspberry pi 3B


time_intervall = 10 # Intervall between two measurements in seconds
plot_time_intervall = 3600 # Intervall between creating plots
average_number = 10	# Average over this number of measurements
start_time_stamp = time.time()	
last_time_stamp = start_time_stamp
plot_time_stamp = start_time_stamp
average_counter = 0;

day = 0

t = []
temperature = []
humidity = []	

def mean(values): # For averaging
	return float(sum(values))/float(max(len(values), 1))
def day(): # Returns day of the month as a float; for example 29.5 means 12 o'clock on the 29th
	lt = time.localtime()
	day= lt.tm_mday + lt.tm_hour/24.0 + lt.tm_min/(60*24.0) + lt.tm_sec/(60*60*24.0)
	return day

while True:
	lt = time.localtime()
	if not os.path.isfile(str(lt.tm_year)+'_'+str(lt.tm_mon)+'_data.txt'): # Create a data file and plot for each month
		print(str(lt.tm_year)+'_'+str(lt.tm_mon)+'_data.txt has been created')
		file = open(str(lt.tm_year)+'_'+str(lt.tm_mon)+'_data.txt', 'w')
		file.close()
	humidity_read, temperature_read = Adafruit_DHT.read_retry(sensor, pin) # Read data from sensor
	t.append(day())
	temperature.append(temperature_read)
	humidity.append(humidity_read)
	average_counter = average_counter +1

	if average_counter >= average_number: # Average and write the average values to a file
		average_counter = 0;
		mean_t = mean(t)
		mean_temperature = mean(temperature)
		mean_humidity = mean(humidity)
		file = open(str(lt.tm_year)+'_'+str(lt.tm_mon)+'_data.txt','a')
		file.write(str(mean_t)+'\t'+str(mean_temperature)+'\t'+str(mean_humidity)+'\t\n')
		file.close()
		t = []
		temperature = []
		humidity = []
		if (time.time()-plot_time_stamp)> plot_time_intervall: # Plotting
			plot_time_stamp = time.time()
			fig, ax1 = plt.subplots()
			file = open(str(lt.tm_year)+'_'+str(lt.tm_mon)+'_data.txt', 'r')
			for line in file:	# Read the data
				read_data = line.split('\t')
				t.append(read_data[0])
				temperature.append(read_data[1])
				humidity.append(read_data[2])
			file.close()	
			# Do the plotting using two axis
			ax1.plot(t, temperature, 'b.')
			ax1.set_xlabel('Day of month '+str(lt.tm_mon)+' '+str(lt.tm_year))
			# Make the y-axis label, ticks and tick labels match the line color.
			ax1.set_ylabel('Temperature [C]', color='b')
			ax1.tick_params('y', colors='b')
			plt.grid(True)
			
			ax2 = ax1.twinx()
			ax2.plot(t, humidity, 'r.')
			ax2.set_ylabel('Humidity [%]', color='r')
			ax2.tick_params('y', colors='r')
			plt.grid(True)
			fig.tight_layout()
			
			plt.savefig('/var/www/html/'+str(lt.tm_year)+'_'+str(lt.tm_mon)+'.png', transparent=True) # Save plot on lighttpd server
			plt.savefig(str(lt.tm_year)+'_'+str(lt.tm_mon)+'.png', transparent=True) # Save second plot

			plt.close()		
			
			t = []
			temperature = []
			humidity = []
			
			if not day == lt.tm_mday: # Upload picture to git every day using a shell script
				day = lt.tm_mday
				os.system('./upload.sh')
	time.sleep(time_intervall)
	

				
