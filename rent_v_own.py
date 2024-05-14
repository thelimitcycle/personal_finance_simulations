import datetime
import numpy as np
import pandas as pd
import pandas_market_calendars as mcal
import characterize_spy
import matplotlib.pyplot as plt

def market_is_open(date):
    result = mcal.get_calendar("NYSE").schedule(start_date=date, end_date=date)
    return result.empty == False


spy_log_returns = characterize_spy.spy_log_returns()
n_returns = len(spy_log_returns)

#parameters 
start_date = datetime.date(2024, 5, 12)
end_date  = datetime.date(2054, 5, 13)
num_days = (end_date - start_date).days  + 1

num_runs = 5000

run_length = sim_length = (end_date - start_date).days + 1
annual_rent_increase = [0.03, 0.05, 0.07]

rent_balance_time_history = np.zeros((len(annual_rent_increase),num_runs, sim_length))
own_cumulative_time_history = np.zeros(sim_length)
rent_cumulative_time_history =  np.zeros((len(annual_rent_increase),sim_length))

#parameters for the simulation
#maybe put these in a .yaml
rent = 4000.00
original_home_price = 1338000.00
#doesn't include 
#-maintenance
#-- look up average maintenance costs for a home in California
#-utilities (but those would be about the same)
monthly_payment = 9853.00

for k in range(len(annual_rent_increase)):
    for i in range(num_runs):
        #set the initial conditions
        current_date = start_date
        day_counter = 0
        rent_balance = monthly_payment
        own_balance = monthly_payment
        rent  = 4000
        total_rent_paid = 0
        total_mortgage_paid = 0

        while current_date <= end_date:
            if(current_date.day == 1):
                # pay rent  or mortgage payment
                rent_balance = rent_balance + (monthly_payment - rent)
                total_rent_paid += rent
                total_mortgage_paid += monthly_payment
            
            if(current_date.month == 5 and current_date.day == 12):
                #increase the rent
                rent  = rent * (1+annual_rent_increase[k])
            
            #get investments returns on your leftover money
            # I think the market_is_open call is slowing things down wait, nvm is probably the random spy call...
                
            #demorgan's laws stoned af
            if((rent_balance > 0) and (current_date.weekday() != 5 and current_date.weekday() !=6)):
                    index = np.random.randint(n_returns)
                    rent_balance  = rent_balance*(np.exp(spy_log_returns[index]))
            
            rent_balance_time_history[k,i,day_counter] = rent_balance
            own_cumulative_time_history[day_counter] = total_mortgage_paid
            rent_cumulative_time_history[k,day_counter] = total_rent_paid
            
            day_counter += 1
            current_date += datetime.timedelta(days=1)

days = np.arange(num_days)

plt.figure()
#plt.plot(rent_balance_time_history.T)
plt.plot(rent_cumulative_time_history[0,:])
plt.plot(rent_cumulative_time_history[1,:])
plt.plot(rent_cumulative_time_history[2,:])
plt.plot(own_cumulative_time_history)
plt.title('rent vs own: cumulative payments')
plt.legend(['cumulative rent payments 0.03 annual increase','cumulative rent payments 0.05 annual increase', 'cumulative rent payments 0.07 annual increase', 'mortgage cumulative payments'])
plt.ylabel('money [USD]')
plt.xlabel('time [days]')
plt.savefig('rent_vs_own_payments.png')
plt.close()

# plt.figure()
# #change color and opacity
# plt.hist(rent_balance_time_history[0,:,num_days-1], bins=75, color="blue", alpha=0.5)
# plt.hist(rent_balance_time_history[1,:,num_days-1], bins=75, color="red", alpha=0.5)
# plt.hist(rent_balance_time_history[2,:,num_days-1], bins=75, color="yellow", alpha=0.5)
# plt.show()

rent_balance_home_price_ratio = rent_balance_time_history[:,:,num_days-1]/original_home_price
rates_of_return = np.power(rent_balance_home_price_ratio,1/30) - 1
#this is where it is blowing up...
ror = rates_of_return[np.logical_not(np.isnan(rates_of_return))]
plt.figure()
plt.title("Annualized Rate of Return on a house required to make owning the same as renting \n n= 5000")
plt.hist(rates_of_return[0,~np.isnan(rates_of_return[0,:])], bins=100, color='blue', alpha=0.3)
plt.hist(rates_of_return[1,~np.isnan(rates_of_return[1,:])], bins=100, color='red',alpha=0.3)
plt.hist(rates_of_return[2,~np.isnan(rates_of_return[2,:])], bins=100, color='yellow',alpha=0.3)
plt.legend(['3 percent annual rent increase', '5 percent annual rent increase','7 percent annual rent increase'])
plt.xlim([-0.1, 0.25])
#plt.savefig('rent_vs_own_annualized_rate_of_return_required_to_beat_renting.png')
plt.show()

#print the scipy deciles for what the annualized rate of return on a has to be to be a better investment
print("Median annualized rate of return required to make owning equal to renting ")
print("0.03 rent increase: " + str(np.percentile(rates_of_return[0,~np.isnan(rates_of_return[0,:])], 50)))
print("0.05 rent increase: " + str(np.percentile(rates_of_return[1,~np.isnan(rates_of_return[1,:])], 50)))
print("0.07 rent increase: " + str(np.percentile(rates_of_return[2,~np.isnan(rates_of_return[2,:])], 50)))