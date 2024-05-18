# Example Home Assistant Integration

This example integration attempts to give a good basic framework for those wishing to develop a HA custom integration but have little knowledge of how to start.

It builds upon the basic scaffold integration code from HA with some enhancements to make it more functional and closer to what is needed to build a functioning integration.

## Can I Run It?

Yes, this is a fully functioning integration (I mean it doesn't do anything as the api is mocked), that will provide a config flow to add the integration and create 4 devices with 2 sensors each (a binary sensor door entity and a temperature sensor entity).

The mocked api is designed to randomly change the door open/closed status and the temp sensor values, so it looks like it is getting actual readings from real devices.

NOTE: For the purposes of being a good example, the api only accepts a specific username and password.  These are prepopulated when adding the integration (do not do this with your own real world integrations!).  If you modify these, you will get an Authorisation error (but thats what should happen if they are wrong!).

## How Do I Install This?

If you are going to start developing integrations, there are some things you need to learn and do first.  These are:

1. Create a HA development environment.  Investing the time to do this at the start will reward you with all that time back and more later.  I highly recommend using the VSCode Dev Container method.
2. Create a github account (it's free) and fork this repository.  That way, you can modify this example to build your own and have a nice safe place to store it, so you do not risk loosing the work you put into it.  Again, VSCode will make it very easy to commit changes to your repository, if you take the time to set it up.
3. Obviously, you are going to need some level of Python knowledge.  If you are like me, walking through existing working examples, is a good way to learn and there is also much on google.  The biggest learning curve (IMHO), is how to get going with an integration.  The development documentation is pretty good in places but I think much more of a reference guide than a step by step getting you going.  That is why I decided to put some time to create this working example that includes the key elements you will need for pretty much any custom integration.

So, once you have ticked off your TODO list above, you can install this by cloning from your fork to your machine.  Only copy the `exampleintegration` folder into your config\custom_components folder.  Once you are a bit more familiar with the development process and the required tools, see advanced note below on how I do it to make my life easier.

## Breaking Down The Code

To follow....

## Advanced Notes

### Advanced How Do I Install This?

In order to simplify my workflow when writing custom components, I have a directory on my machine that all developed custom components have a folder under.  This allows me to manage my git workflow via this folder seperate from the HA Dev Container as there are more files to include in an overall repository that what goes into custom_components (this README.md for example!).

I then modify my devcontainer.json file (the one provided by HA to create you dev container) and mount this developed custom components directory to config/share within the dev container.
From that I can create a symlink to place the correct folder in custom components.

Sounds confusing??  Ok....So I have a folder structure:

```text
  development
    |_integrationAFolder
        |_custom_components
          |_integrationA
    |_integrationBFolder
        |_custom_components
          |_integrationA
    |-etc
```

The integrationXFolder level is the one that relates to your github repo.

Then to be able to access this in my VSCode Dev Container, I add the following to the devcontainer.json file, just under the RunArgs line (currently around line 16).

```text
"mounts": [
  "source=${localEnv:HOME}/development,target=${containerWorkspaceFolder}/share/development,type=bind",
],
```

You will then need to rebuild your dev container and this folder will now appear under config/share in your dev container.

To then symlink my custom integration into the config/custom_components folder, do the following in a terminal session inside the dev container.

```text
cd /workspaces/core/config/custom_components
ln -s /workspaces/core/share/development/integrationAFolder/custom_components/integrationA integrationA
```

And hey presto, when you run (or restart if already running) the Home Assistant server in your dev container, the integration will load and you will be able to add it via Devices & Services.
