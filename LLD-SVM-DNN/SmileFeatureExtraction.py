#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 13 15:40:12 2019

@author: zhuzhi
"""

import os
import socket
import shutil
import subprocess
import pandas as pd
from utils import load_IEMOCAP


def SmileExtract(smilePath, configPath, configs, database, dataDf):
    for config in configs:
        smileConfig = configPath + configs[config]
        featureFile = "features/{}_{}.csv".format(database, config)
        print("Extracting {} feature set.".format(config))
        N = dataDf.shape[0]
        n = 0
        for _, row in dataDf.iterrows():
            cmd = ('{0} -C "{1}" -I "{2}" -csvoutput "{3}" -instname '
                   + '"{4}" -l 0').format(smilePath, smileConfig,
                                          row.soundPath, featureFile,
                                          row.soundPath)
            subprocess.Popen(cmd, shell=True,
                             stdout=subprocess.PIPE).communicate()
            print("\r{}% finished.".format(round((n+1)/N*100, 2)), end="")
            n += 1
        print()
        featureDf = pd.read_csv("features/{}_{}.csv".format(database, config),
                                sep=";")
        featureDf.drop("frameTime", axis=1, inplace=True)
        featureDf["emotion"] = dataDf.emotion
        featureDf["speaker"] = dataDf.speaker
        if "actType" in dataDf.columns:
            featureDf["actType"] = dataDf.actType
            featureDf.set_index(["actType", 'speaker', 'emotion', 'name'],
                                inplace=True)
        else:
            featureDf.set_index(['speaker', 'emotion', 'name'],
                                inplace=True)
        featureDf.sort_index(inplace=True)
        featureDf.to_csv(featureFile)


def main():
    # define paths of SMILExtract, configs of open simle, and IEMOCAP database
    if socket.getfqdn(socket.gethostname()) == "d8":
        smilePath = "/home/zhu/Library/opensmile/bin/SMILExtract"
        configPath = "/home/zhu/Library/opensmile-2.3.0/config/"
    else:
        smilePath = "/usr/local/bin/SMILExtract"
        configPath = "/Users/zhuzhi/Library/opensmile-2.3.0/config/"
    dataPath = "../../../Database/IEMOCAP_full_release/"
    # SIMLE configs
    configs = {"IS09": "IS09_emotion.conf",
               "IS10": "IS10_paraling.conf",
               "IS11": "IS11_speaker_state.conf",
               "IS12": "IS12_speaker_trait.conf",
               "ComParE": "IS13_ComParE.conf",
               "GeMAPS": "gemaps/GeMAPSv01a.conf",
               "eGeMAPS": "gemaps/eGeMAPSv01a.conf"}
    # emotions and acting types
    database = "IEMOCAP"
    emotionsTest = ["Neutral", "Happiness", "Sadness", "Anger"]
    actTypeToUse = ["impro"]
    # extraction
    shutil.rmtree("features", ignore_errors=True)
    os.mkdir("features")
    dataDf = load_IEMOCAP(dataPath, actTypeToUse, emotionsTest)
    SmileExtract(smilePath, configPath, configs, database, dataDf)


if __name__ == "__main__":
    main()
