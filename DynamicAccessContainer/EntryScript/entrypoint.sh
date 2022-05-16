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
if [ -z "$ENVIRONEMT_ID" ];
then
    echo "ENVIRONEMT_ID variable is is empty"
fi

echo "*** Register the BZero target ***"
bzero-beta -serviceUrl $SERVICE_URL -activationToken $ACTIVATION_TOKEN -environmentId $ENVIRONEMT_ID

echo "*** Start the BZero agent ***"
bzero-beta