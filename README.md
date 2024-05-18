# Example Home Assistant Integration

This example integration attempts to give a good basic framework for those wishing to develop a HA custom integration but have little knowledge of how to start.

It builds upon the basic scaffold integration code from HA with some enhancements to make it more functional and closer to what is needed to build a functioning integration.

## Can I Run It?
Yes, this is a fully functioning integration (I mean it doesn't do anything as the api is mocked), that will provide a config flow to add the integration and create 4 devices with 2 sensors each (a binary sensor door entity and a temperature sensor entity).

The mocked api is designed to randomly change the door open/closed status and the temp sensor values, so it looks like it is getting actual readings from real devices.

NOTE: For the purposes of being a good example, the api only accepts a specific username and password.  These are prepopulated when adding the integration.  If you modify these, you will get an Authorisation error (but thats what should happen if they are wrong!


## Breaking Down The Code

To follow....