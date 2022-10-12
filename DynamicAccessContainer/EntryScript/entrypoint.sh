#!/bin/sh

# Ensure we have the needed Enviormental variables
if [ -z "$ACTIVATION_TOKEN" ];
then
    echo "ACTIVATION_TOKEN variable is is empty"
fi 
if [ -z "$SERVICE_URL" ];
then
    echo "SERVICE_URL variable is is empty"
fi 
if [ -z "$ENVIRONMENT_ID" ];
then
    echo "ENVIRONMENT_ID variable is is empty"
fi

echo "*** Register the BZero target ***"
bzero -serviceUrl $SERVICE_URL -activationToken $ACTIVATION_TOKEN -environmentId $ENVIRONMENT_ID

echo "*** Start the BZero agent ***"
bzero