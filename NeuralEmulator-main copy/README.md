# NeuralEmulator
OZ neural emulator
The OZ neural emulator is a scalable Python framework for building, testing, and deploying Spiking Neural Networks architecture and learning algorithms that are using our OZ, PES, and STDP analog circuits designs as the main building blocks. 
The OZ neural emulator can give us a clue if our methods are in the right direction, without the need for expensive hardware deployments and with less time wasted in the hardware circuits design in a CAD tool and the simulation time (SPICE).
 Moreover, as the number of neurons increases the SPICE simulation runtime is not reasonable, so we aim to balance emulation accuracy against scalability.
Each of the building blocks that were mentioned earlier was divided into a sub-building block, where each sub-building have a corresponding model that was created using its SPICE simulation with varying input signals.
 For example, the Pulse-current synapse model has two inputs VIN and VW, constant VDD and IOUT as output.
Therefore, its model should look like the following F(VIN, VW)= IOUT.
The OZ neuron model has (among others) the Pulse-current synapse as a sub-building block that can be changed.
To build the Pulse-current synapse model we simulate its circuit design in a SPICE simulator where each of its input range between 0-VDD with 10mv step.
When the Pulse-current synapse Python model will be created we will pass the SPICE results wrapped with an Interface class that will perform the processing of the SPICE simulation output file and will provide a query-like interface for a given pair of (VIN, VW).
Because the SPICE output file is sorted by the VIN, VW values, we decided to use the Binary Search to provide the output current of the model.
Each model in the OZ neural emulator is implementing one of the two main interfaces, a VoltageSource or CurrentSource, where each class has a pure virtual function GetVoltage or GetCurrent.
Following the previous example, the Pulse-current synapse is deriving the CurrentSource class, because it provides current that can be used as input to another model.
The OZ neural emulator is a time base simulation, meaning the simulation will run for a predefined number of seconds, where each simulation cycle is also predefined, i.e there will (SIM_TIME/SIM_CYCLE_TIME) steps.
To enforce a uniform interface for the simulation scheduler, VoltageSource and CurrentSource classes are deriving an interface name SimBase, which has a pure virtual function name Run.
At each step, the simulation scheduler goes over a list of SimBase objects, and just activating the Run function, the SimBase object’s structure (network design) is up to the user to define, I.e., the iteration order. In the future, we would like to add multi-threading capabilities to the scheduler to fasten each layer run.
Each SimBase object in the simulation is aware of the simulation cycle time via a configuration class, and its responsibility is to process the input data he received via ether VoltageSource or CurrentSource or both, at each Run call and store the corresponding result for when some will use the interface it implementing as discussed earlier, with O(SIM_CYCLE_TIME/totalNumberOfSimBaseObjects) run time.
For example, at each step the scheduler will trigger the Pulse-current synapse model Run function, the Run function implementation will be to take the input voltages VIN, VW values via two VoltageSource objects that were given during Pulse-current synapse creation, with the GetVoltage function. It will then use its model to calculate the output current IOUT and will store the received value.
 The OZ neuron is composed of a Pulse-current synapse object, i.e with a CurrentSource object. In the OZ Run function implementation, it will use the GetCurrent of the CurrentSource object it received during the construction time, to calculate the frequency of the spikes. Therefore, in the network construction, we need to ensure that the model of Pulse-current synapse will run before the OZ neuron with some structure like the trivial layers that are used in the classic artificial neural networks. These are the basic principles of the OZ neural emulator, 
and a full class diagram is provided in “A”.


