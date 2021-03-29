#!/bin/sh

# Ensure we have the needed Enviormental variables
if [ -z "$ACTIVATION_ID" ];
then
    echo "ACTIVATION_ID variable is is empty"
fi 
if [ -z "$ACTIVATION_CODE" ];
then
    echo "ACTIVATION_CODE variable is is empty"
fi 
if [ -z "$ACTIVATION_REGION" ];
then
    echo "ACTIVATION_REGION variable is is empty"
fi 
if [ -z "$ORG_ID" ];
then
    echo "ORG_ID variable is is empty"
fi 
if [ -z "$ORG_PROVIDER" ];
then
    echo "ORG_PROVIDER variable is is empty"
fi 

echo "*** Registering the instance using the clunk80 SSM Agent ***"
sudo bzero-ssm-agent -register -code $ACTIVATION_CODE -id $ACTIVATION_ID -region $ACTIVATION_REGION -org $ORG_ID -orgProvider $ORG_PROVIDER

echo "*** Restarting the clunk80 SSM Agent ***"
bzero-ssm-agent