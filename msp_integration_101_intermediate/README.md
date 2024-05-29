# Integration 101 Intermediate Example

This is a slightly more advanced integration built on top of the Integration 101 Template.  If you are new to writing integrations, it is highly recommended to start with the Integration 101 Template and get your integration working to talk to your api and generate some sensor entities, before adding some of these more advanced elements to control functions of your api/devices.

Even if you are more adept, it still might be worth reviewing the Integration 101 Template first to familiarise yourself with how it is built up to this intermediate example.

### What does it show?

It adds the following things to the original basic example.

- More advanced config flow, demonstrating multi-step configs, using selectors and using your api data in the flow.
- Services - both integration and entity services.  More about the differences of these below.
- A base entity class that all entity types inherit, to show how you can save code for common entity properties.
- Examples of using _attr_* attributes in your entity platform classes to set entity properties and reduce code.
- Switches, lights and fan entity types

It also allows you to play around with this code to see how those changes impact the integration, knowing you are working from a good start point.

### Does it work?

Yes, it is fully functional in the Home Assistant UI, except the api is mocked, so doesn't do anything for real!  However, if you use the switches and lights, you will see other sensors change as they would in a real situation.

## Further Explanaitions

## Services

So, as stated above, there are 2 types of services, Integration Services and Entity Services.  They are pretty similar in creating a service but have nuances in use and are setup slightly differently.

However, in both of these service types, you need to have a services.yaml file with a set of keys that define some properties like name, description etc and also definitions for your fields which drive how they appear in the UI Developer console.

This Intermediate Example has 3 services:
- 1 Entity Service
- 1 Integration Service
- 1 Integration Service with a Response

along with an example service.yaml file to match, so you can see how to create each one in code.

NOTE:  Home Assistant does come with many built in services to control many functions of devices.  Before diving in to create your own, make sure that one doesn't already exist, otherwise you can make your integration more complicated to use by not supporting the serivces expected by your users.

### Integration Services

These are setup at your integration level and perform any function you wish.

Unlike Entity Serivces, you can have a service that does not require an entity to be selected. For example, if you wanted to send a command to your api, your service can just require the user select the command and it will send it.  They can be used to perform functions on some of your entities but it is easier to use Entity services for that.

### Entity Services

These are setup within your entity platform and are specifically for calling a service on an entity or group of entities.

These services automatially request an entity id, device, area or label and as such, you could not perform the same example as above.

The service will be called on entities that match the selected target (area, device, entity or label) and therefore it can run on multiple entities at the same time.  If that entity does not have the function specified in the service, nothing will happen.  Ie, no action will be performed and no error will be raised.  You can this service being called on multiple entities in this example by adding the same label to the 2 lights or put them in the same area and select that label or area when calling the service. Turn on debug logging to see the devices that got updated.

If you want to use this Entity Service on multiple platforms (ie lights and switches), you have to define it in each platform separately.  It is also recommended that if you do this, make the service definition exactly the same or you will run into issues.

An example of use for this is that you want to send a command to one or many lights on your integration, such as setting an off timer (as per our example in the code).  In which case, you would pick an entity relating to a specific light, or select an area to send the command to all lights in that area.

See within lights.py for a commented code example of this.