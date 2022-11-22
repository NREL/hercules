// test_client.c
//
// Small code example to illustrate how we could get 0mq into c/c++
// I think it's possible I'm mixing c and c++ but if it works?
// Paul Fleming, 2022
//
// NOTES HERE
// On my mac starting with
// STARTING WWITH brew install czmq
// Suspect this isn't necessary on eagle?
//  g++ -Wall -g test_client.c -lzmq -o test_client



// Libraries I'm apparantly using...
// This could also probably be cut down but for now

#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <cstdio>
// #include <string.h>
// #include <helics/cpp98/ValueFederate.hpp>
#include <helics/cpp98/CombinationFederate.hpp>
// #include <helics/cpp98/MessageFederate.hpp>
#include <helics/cpp98/helics.hpp>
#include <cmath>
#include <iostream>
#include <string>
#include <sstream>
#include <list>

void tokenize(std::string s, std::string del, std::list<double> &return_list)
{

  int start = 0;
  int end = s.find(del);

  return_list.push_front(atof(s.substr(start + 1, end - start).c_str()));
  while (end > 0)
  {

    start = end + del.size();
    end = s.find(del, start);

    if (end == -1)
      end = -2;
    return_list.push_front(atof(s.substr(start, end - start).c_str()));
  }
};

int main(void)
{

  std::string fedinitstring = "--federates=1";
  double deltat = 0.01;
  helicscpp::Input sub;

  helicscpp::Publication pub;

  //   printf("PI RECEIVER: Helics version = %s\n", helicsGetVersion());

  /* Create Federate Info object that describes the federate properties
   * Set federate name and core type from string
   */
  helicscpp::FederateInfo fi("zmq");

  /* Federate init string */
  fi.setCoreInit(fedinitstring);

  /* Set the message interval (timedelta) for federate. Note that
     HELICS minimum message time interval is 1 ns and by default
     it uses a time delta of 1 second. What is provided to the
     setTimedelta routine is a multiplier for the default timedelta.
  */
  /* Set one second message interval */

  /* Create value federate */
  helicscpp::CombinationFederate vfed("Test receiver Federate", fi);
  printf("PI RECEIVER: Value federate created\n");

  vfed.setProperty(HELICS_PROPERTY_TIME_DELTA, 1.0);
  /* Subscribe to PI SENDER's publication */
  sub = vfed.registerSubscription("control", "string");
  printf("PI RECEIVER: Subscription registered\n");

  /* Register the publication */
  pub = vfed.registerGlobalPublication("status", "string");
  printf("PI RECEIVER: Publication registered\n");

  fflush(NULL);
  /* Enter initialization state */
  vfed.enterInitializingMode(); // can throw helicscpp::InvalidStateTransition exception
  printf("PI RECEIVER: Entered initialization state\n");

  // Variables
  float wind_speed = 6.0;       // float containing the wind speed back from control center
  float wind_direction = 290.0; //float containing the wind direction back from control center
  const int num_turbines = 4;

  std::string strToControlCenter; // String that gets sent to ControlCenter
  // char charFromControlCenter[9900]; // char array of what we got back from ControlCenter

  // Declare an array of turbine powers
  float turbine_power_array[num_turbines] = {0, 0, 0, 0};
  /* Enter execution state */
  HelicsTime currenttime = 0.0;
  vfed.enterExecutingMode(); // can throw helicscpp::InvalidStateTransition exception
  printf("PI RECEIVER: Entered execution state\n");

  printf("Connecting to ControlCenter...\n");
  printf("Connected..., entering simulation\n");

  // Make initial connection to control center to receive the wind speed
  // and wind direction to use in the 0th time step
  std::stringstream ssInitialCode;                             // stringStream used to hold initial code
  ssInitialCode << "[" << -1 << "," << -1 << "," << -1 << "]"; // code should be an array with to -1 values
  strToControlCenter = ssInitialCode.str();                    //Convert to a string
  std::cout << "initial message to control center: [" << strToControlCenter << "] \n";

  // Send the data to the control center

  currenttime = vfed.getCurrentTime();
  std::cout << "time now " << currenttime << "\n ";
  pub.publish(strToControlCenter);


  // length of simulation
  int simulation_endtime = 10;

  std::stringstream charFromControlCenter;
  charFromControlCenter << sub.getString().c_str();

  // // This loop is meant to simulate the stepping of AMR Wind
  int time_step;

  while (currenttime < simulation_endtime)
  {
    //   for (time_step = 0; time_step > -1; time_step++) {  // Never stop
    time_step = currenttime;
    // Start the time step
    std::cout << "CURRENT TIME" << currenttime << " TIME STEP :" << time_step << std::endl;

    std::stringstream charFromControlCenter;
    charFromControlCenter << sub.getString().c_str();

    std::stringstream ss(charFromControlCenter.str());
    std::cout << "Received data from control center " << charFromControlCenter.str() << std::endl;

    // ss >> wind_speed;  // This seems to work, I'm not positive it should?  wind_speed is a float but ss is a string?  maybe c++ magic?
    // ss >> wind_direction; // This seems to work, I'm not positive it should?  wind_speed is a float but ss is a string?  maybe c++ magic?
    // std::cout << "...wind speed: " << wind_speed << "\n";
    // std::cout << "...wind direction: " << wind_direction << "\n"; // This seems to work, I'm not positive it should?  wind_speed is a float but ss is a string?  maybe c++ magic?

    // std::cout <<"Print received wind_speed variable "<< wind_speed << " direction " << wind_direction<< std::endl;

    if (currenttime > 0)

    {
        // Igonre timestep 0 since message pipe has junk. 
        // // Unpack the values from the control center using a string stream

      std::list<double> return_list;
      tokenize(charFromControlCenter.str(), ",", return_list);

      wind_direction = return_list.front();
      return_list.pop_front();
      wind_speed = return_list.front();
      return_list.pop_front();
    }

    // This would be the point AMR Wind simulates time step time_step
    // Using a stand in equation
    turbine_power_array[0] = wind_speed * wind_speed * wind_speed + 100.0;
    turbine_power_array[1] = wind_speed * wind_speed * wind_speed + 50.0;
    turbine_power_array[2] = wind_speed * wind_speed * wind_speed * 3 / 5 + 50;
    turbine_power_array[3] = wind_speed * wind_speed * wind_speed * 3 / 5;

    // Now communicate with the control center to get wind speed and
    // wind direction for the next time step

    // Build the message to send to the Control Center using string operations
    // Note the message includes a space between each value
    std::stringstream ssToControlCenter; // stringStream used to construct strToSSC
    ssToControlCenter << "[";
    ssToControlCenter << time_step << ",";  // First entry is timestep
    ssToControlCenter << wind_speed << ","; // First entry is wind_speed
    ssToControlCenter << wind_direction;    // First entry is wind_direction
    // Next the turbine information
    for (int i = 0; i < num_turbines; i++)
    {
      ssToControlCenter << "," << turbine_power_array[i];
    }
    ssToControlCenter << "]";
    strToControlCenter = ssToControlCenter.str(); //Convert to a string
    std::cout << "message to control center: " << strToControlCenter << std::endl;

    // Send the data to the control center
    pub.publish(strToControlCenter.c_str());

    currenttime = vfed.requestNextStep();
    time_step = currenttime;

    std::cout << "...wind speed: " << wind_speed << "\n";
    std::cout << "...wind direction: " << wind_direction << "\n";
  }

  vfed.finalize();

  return 0;
}
