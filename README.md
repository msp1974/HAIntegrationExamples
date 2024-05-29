# Example Home Assistant Integration

These example integrations attempt to give a good basic framework for those wishing to develop a HA custom integration but have little knowledge of how to start.

There are 3 main integrations here as follows:

## Integration 101 Template

  This is (in my view) the basic building blocks to get started on your own integration.  It will need some modifications by you to suit your own specifics but it shows how to:

- Integration Initialisation
  - The basic steps to initialise your integration
  - Adding a listener to reload your integration if options change
  - Adding the option to delete devices in the UI

- Config Flow
  - Create a basic config flow to setup your integration via the UI
  - Create a config flow to reconfigure your integration
  - Creat an options flow to allow setting of optional parameters

- Using a DataUpdateCoordinator 
  - How to setup a data coordinator to manage communication with your api
  - How to store and use that data across your entity platforms

- Entity platforms
  - Examples of adding binary sensors
  - Examples of adding sensors

## Integration 101 Intermediate

This builds on the Integration 101 Template and adds some more advanced functionality to help make your integration more functional:

- Config Flow
  - Multi-step flows
  - Using selectors in your flows
  - Using data from your api in a config flow

- Entity Platforms
  - Setting up switches, lights and fans as examples of entites that can control your devices
  - Using `_attr_*` attributes in your entity classes to reduce code size

- Base Entity
  - Using a base entity from which to inherit all your entity classes to make you code smaller and neater

- Services
  - Entity services to call against your entities
  - Integration services to call against your integration/api

## Integration 101 Advanced

This is currently a work in progress but will add the following to the Integration 101 Intermediate example.

- Translations
- Websockets
- Firing Events
- Device Triggers for automations
- And maybe more... (please raise and issue to see a subject covered)


## Can I Run Them?

Yes, these are fully functioning integrations (I mean they don't do anything as the api is mocked), that will provide a config flow to add the integration and create devices with entities.

In the Integration 101 Template, the mocked api is designed to randomly change the door open/closed status and the temp sensor values, so it looks like it is getting actual readings from real devices.  The Integration 101 Intermedate and Advanced don't do this.

NOTE: For the purposes of being a good example, the api only accepts a specific username and password.  These are prepopulated when adding the integration (do not do this with your own real world integrations!).  If you modify these, you will get an Authorisation error (but thats what should happen if they are wrong!).

## How Do I Install This?

If you are going to start developing integrations, there are some things you need to learn and do first.  These are:

1. **Create a HA development environment**

   Investing the time to do this at the start will reward you with all that time back and more later.  I highly recommend using the VSCode Dev Container method.

   [Developing with Visual Studio Code and Devcontainer](https://developers.home-assistant.io/docs/development_environment#developing-with-visual-studio-code--devcontainer)

2. **Create a github account (it's free) and fork this repository**

    That way, you can modify this example to build your own and have a nice safe place to store it, so you do not risk loosing the work you put into it.  Again, VSCode will make it very easy to commit changes to your repository, if you take the time to set it up.

3. **Obviously, you are going to need some level of Python knowledge**

    If you are like me, walking through existing working examples, is a good way to learn and there is also much on google.  The biggest learning curve (IMHO), is how to get going with an integration.  The development documentation is pretty good in places but I think much more of a reference guide than a step by step getting you going.  That is why I decided to put some time to create this working example that includes the key elements you will need for pretty much any custom integration.

So, once you have ticked off your todo list above, you can install one of these examples by cloning from your fork to your machine.  You can copy all the folders into your config\custom_components folder or just choose one.  Once you are a bit more familiar with the development process and the required tools, see advanced note below on how I do it to make my life easier.

## Starting to Code Your Own Integration

These example integrations are basic foundations for an integration.  It is unlikely that you can just copy it, make a few tweaks and off you go.  However, it tries to demonstrate many of the HA concepts that most integrations would need.

If you are starting out using this example, I would recommend taking the following path.  In each step, add logging output to help you see what is going on - use simple text to show you have reached a point in a function, output api responses, variable values etc.

1. Establish the link to your api and configure the minimum set of parameters in your config flow to connect to it.
2. Think about the data format you will have from your api and develop your DataUpdateCoordinator to capture and store that data in a way that makes it easier to use in your entities.
3. Start adding your entities (and device definitions), one type at a time to ensure you are happy that they are being created/functioning correctly as you go.
4. Now you can add more complexity with more config flow parameters, config flow options etc, automation triggers etc.

## Breaking Down The Code

Each example folder has a README file in which I have tried to explain each of the main elements.  I have also commented the code to provide explanaitions of what is happening and what you should change for your own integration.

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
