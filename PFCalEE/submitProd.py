#!/usr/bin/env python

import os,sys
import optparse
import commands
import math
import random

git_tag=os.popen('git describe --tags --abbrev=0').read()

usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-s', '--short-queue' ,    dest='squeue'             , help='short batch queue [%default]' , default='tomorrow')
parser.add_option('-q', '--long-queue'  ,    dest='lqueue'             , help='long batch queue [%default]'  , default='nextweek')
parser.add_option('-t', '--git-tag'     ,    dest='gittag'             , help='git tag version [%default]'   , default=git_tag)
parser.add_option('-r', '--run'         ,    dest='run'                , help='stat run'                     , default=-1,      type=int)
parser.add_option('-v', '--version'     ,    dest='version'            , help='detector version'             , default=3,      type=int)
parser.add_option('-m', '--model'       ,    dest='model'              , help='detector model'               , default=3,      type=int)
parser.add_option(      '--granularity' ,    dest='granularity'        , help='lateral granularity (0=HD,1=LD) [%default]', default=1,      type=int)
parser.add_option('-a', '--eta'         ,    dest='eta'                , help='incidence eta'                , default=0,      type=float)
parser.add_option('-p', '--phi'         ,    dest='phi'                , help='incidence phi angle in pi unit' , default=0.5,      type=float)
parser.add_option('-b', '--Bfield'      ,    dest='Bfield'             , help='B field value in Tesla'       , default=0,      type=float)
parser.add_option('-d', '--datatype'    ,    dest='datatype'           , help='data type or particle to shoot', default='e-')
parser.add_option('-f', '--datafile'    ,    dest='datafile'           , help='full path to HepMC input file', default='')
#data/example_MyPythia.dat')
parser.add_option('-F', '--datafileeos'    ,    dest='datafileeos'           , help='EOS path to HepMC input file', default='')
#/eos/cms/store/cmst3/group/hgcal/HGCalMinbias/Pythia8/')
parser.add_option('-n', '--nevts'       ,    dest='nevts'              , help='number of events to generate' , default=1000,    type=int)
parser.add_option('-o', '--out'         ,    dest='out'                , help='output directory'             , default=os.getcwd() )
parser.add_option('-e', '--eos'         ,    dest='eos'                , help='eos path to save root file to EOS',         default='')
parser.add_option('-g', '--gun'         ,    action="store_true",  dest='dogun'              , help='use particle gun.')
parser.add_option(      '--enList'      ,    dest='enList'              , help='E_T list to use with gun [%default]', default='5,10,20,30,40,60,80,100,150,200')
parser.add_option('-S', '--no-submit'   ,    action="store_true",  dest='nosubmit'           , help='Do not submit batch job.')
(opt, args) = parser.parse_args()


random.seed()
if opt.run: random.seed(opt.run)

#for run in `seq 0 19`; do ./submitProd.py -s 2nd -q 1nw -g -S -t testV8 -r $run -v 63 -m 2 -a 1.7 -b 3.8 -d gamma -n 250 -o /afs/cern.ch/work/a/amagnan/public/HGCalTDR/ -e /store/cmst3/group/hgcal/HGCalTDR; done
#for run in `seq 0 49`; do ./submitProd.py -s 2nd -q 2nd  -t testV8 -r $run -v 63 -m 2  -b 3.8 -d HggLarge -n 100 -o /afs/cern.ch/work/a/amagnan/public/HGCalTDR/ -e /store/group/dpg_hgcal/comm_hgcal/amagnan/HGCalTDR -f /afs/cern.ch/work/a/amagnan/public/HepMCFiles/ggHgg_run$run.dat -F ""; done
#for run in `seq 0 1999`; do ./submitProd.py -s 2nd -q 2nd  -t V08-01-00 -r $run -v 63 -m 2 -b 3.8 -d MinBiasLarge -n 1000 -o /afs/cern.ch/work/a/amagnan/public/HGCalTDR/ -e /store/group/dpg_hgcal/comm_hgcal/amagnan/HGCalTDR -f MinBias_run$run.dat; done
#for run in `seq 0 9`; do ./submitProd.py -s 1nd -q 2nd -g -t testCu -r $run -v 65 -m 3 -a 2.0 -b 0 -d gamma -n 500 -o /afs/cern.ch/work/a/amagnan/public/HGCalTDR/ -e /store/group/dpg_hgcal/comm_hgcal/amagnan/HGCalTDR; done

#1 = hexagons, 2=diamonds, 3=triangles, 4=squares
shape=1

enlist=[0]
if opt.dogun : 
    # list of Etransverse, not energy...
    #enlist=[3,5,7,10,20,30,40,50,60,70,80,90,100,125,150,175,200]
    #enlist=[5,10,20,30,40,60,80,100,150,200]
    #enlist=[5,10,20,30,50,70,100]
    enlist=[float(x) for x in opt.enList.split(',')]

#hgg seeds
#for seed in 1417791355 1417791400 1417791462 1417791488 1417791672 1417791741 1417791747 1417791766 1417791846
#command:
#run=1; for seed in 1417791355 1417791400 1417791462 1417791488 1417791672 1417791741 1417791747 1417791766 1417791846; do ./submitProd.py -s 1nw -q 1nw -t V00-02-14 -v 12 -m 2 -d Hgg -f /afs/cern.ch/work/a/amagnan/public/HepMCFiles/ggHgg_${seed}.dat -r ${run} -n 1300 -o /afs/cern.ch/work/a/amagnan/public/HGCalEEGeant4/ -e /store/cmst3/group/hgcal/HGCalEEGeant4; let run=$run+1; done
#vbfHgg seeds
#for seed in 1420833683 1420833689 1420833693 1420833695 1420833696 1420833717

##30
wthick=''
#1.75,1.75,1.75,1.75,1.75,2.8,2.8,2.8,2.8,2.8,4.2,4.2,4.2,4.2,4.2'
pbthick=''
#1,1,1,1,1,2.1,2.1,2.1,2.1,2.1,4.4,4.4,4.4,4.4'
dropLayers=''
label=''
#label='v5_30'
##28
#wthick='1.75,1.75,1.75,1.75,1.75,2.8,2.8,2.8,2.8,2.8,4.2,4.2,4.2,4.2,4.2'
#pbthick='1,1,1,1,1,2.1,2.1,2.1,2.1,2.1,4.4,4.4,5.6,5.6'
#droplayers='25,27'
#label='v5_28'
##24
#wthick='1.75,1.75,1.75,1.75,1.75,2.8,2.8,2.8,2.8,2.8,4.2,4.2,4.2,4.2,4.2'
#pbthick='2.2,2.2,1,1,2.2,2.1,2.1,3.3,2.1,2.1,4.4,4.4,5.6,5.6'
#droplayers='1,3,10,15,25,27'
#label='v5_24'
##18
#wthick='1.75,1.75,1.75,1.75,1.75,2.8,2.8,2.8,2.8,2.8,4.2,4.2,4.2,4.2,4.2'
#pbthick='2.2,2.2,2.2,2.2,2.2,2.2,2.1,3.3,3.3,3.3,4.4,5.6,5.6,5.6'
#droplayers='1,3,5,7,10,12,15,18,20,23,25,27'
#label='v5_18'


for et in enlist :

    nevents=opt.nevts
    #if et>25 and et<70: nevents=nevents/2
    #if et>=70: nevents=200

    myqueue=opt.lqueue
    if et>0 and et<60 : myqueue=opt.squeue
    if et>=60 : myqueue=opt.lqueue
    
    bval="BOFF"
    if opt.Bfield>0 : bval="BON" 
    
    outDir='%sgit_%s/version_%d/model_%d/%s/%s'%(opt.out,opt.gittag,opt.version,opt.model,opt.datatype,bval)
    if len(label)>0: outDir='%s/%s'%(outDir,label) 
    if et>0 : outDir='%s/et_%d'%(outDir,et)
    eosDir='/eos/cms%s/git%s/%s'%(opt.eos,opt.gittag,opt.datatype)
    if opt.eta>0 : outDir='%s/eta_%3.3f'%(outDir,opt.eta)
    if opt.phi!=0.5 : outDir='%s/phi_%3.3fpi'%(outDir,opt.phi) 
    if (opt.run>=0) : outDir='%s/run_%d'%(outDir,opt.run)

    os.system('mkdir -p %s'%outDir)

    #wrapper
    scriptFile = open('%s/runJob.sh'%(outDir), 'w')
    scriptFile.write('#!/bin/bash\n')
    scriptFile.write('localdir=`pwd`\n')
    scriptFile.write('export HOME=%s\n'%(os.environ['HOME']))
    scriptFile.write('cd %s/\n'%(os.getcwd()))
    scriptFile.write('source g4env.sh\n')
    scriptFile.write('cd $localdir\n')
    #scriptFile.write('cd %s\n'%(outDir))


    if len(opt.datafileeos)>0:
        scriptFile.write('eos cp %s/%s %s\n'%(opt.datafileeos,opt.datafile,opt.datafile))

    scriptFile.write('cp %s/g4steer.mac .\n'%(outDir))
    cmd='PFCalEE g4steer.mac --model %d --version %d --eta %f --shape %d'%(opt.model,opt.version,opt.eta,shape)
    if len(wthick)>0 :       cmd += ' --absThickW {}'.format(wthick)
    if len(pbthick)>0 :      cmd += ' --absThickPb {}'.format(pbthick)
    if len(dropLayers)>0 :   cmd += ' --dropLayers {}'.format(dropLayers)
    if not opt.granularity : cmd += ' --fineGranularity'
    scriptFile.write(cmd + '\n')
    outTag='%s_version%d_model%d_%s'%(label,opt.version,opt.model,bval)
    if et>0 : outTag='%s_et%d'%(outTag,et)
    if opt.eta>0 : outTag='%s_eta%3.3f'%(outTag,opt.eta) 
    if opt.phi!=0.5 : outTag='%s_phi%3.3fpi'%(outTag,opt.phi) 
    if (opt.run>=0) : outTag='%s_run%d'%(outTag,opt.run)
    scriptFile.write('mv PFcal.root HGcal_%s.root\n'%(outTag))
    scriptFile.write('echo "--Local directory is " $localdir >> g4.log\n')
    scriptFile.write('echo home=$HOME >> g4.log\n')
    scriptFile.write('echo path=$PATH >> g4.log\n')
    scriptFile.write('echo ldlibpath=$LD_LIBRARY_PATH >> g4.log\n')
    scriptFile.write('ls -ltrh * >> g4.log\n')
    if len(opt.eos)>0:
        #scriptFile.write('grep "alias eos=" /afs/cern.ch/project/eos/installation/cms/etc/setup.sh | sed "s/alias /export my/" > eosenv.sh\n')
        #scriptFile.write('source eosenv.sh\n')
        scriptFile.write('eos mkdir -p %s\n'%eosDir)
        scriptFile.write('eos cp HGcal_%s.root %s/HGcal_%s.root\n'%(outTag,eosDir,outTag))
        scriptFile.write('if (( "$?" != "0" )); then\n')
        scriptFile.write('echo " --- Problem with copy of file PFcal.root to EOS. Keeping locally." >> g4.log\n')
        scriptFile.write('else\n')
        scriptFile.write('eossize=`eos ls -l %s/HGcal_%s.root | awk \'{print $5}\'`\n'%(eosDir,outTag))
        scriptFile.write('localsize=`ls -l HGcal_%s.root | awk \'{print $5}\'`\n'%(outTag))
        scriptFile.write('if [ $eossize != $localsize ]; then\n')
        scriptFile.write('echo " --- Copy of sim file to eos failed. Localsize = $localsize, eossize = $eossize. Keeping locally..." >> g4.log\n')
        scriptFile.write('else\n')
        scriptFile.write('echo " --- Size check done: Localsize = $localsize, eossize = $eossize" >> g4.log\n')
        scriptFile.write('echo " --- File PFcal.root successfully copied to EOS: %s/HGcal_%s.root" >> g4.log\n'%(eosDir,outTag))
        scriptFile.write('rm HGcal_%s.root\n'%(outTag))
        scriptFile.write('fi\n')
        scriptFile.write('fi\n')

    scriptFile.write('echo "--deleting core files and hepmc files: too heavy!!"\n')
    scriptFile.write('rm core.*\n')
    if len(opt.datafileeos)>0:
        scriptFile.write('rm %s\n'%(opt.datafile))
    scriptFile.write('cp * %s/\n'%(outDir))
    scriptFile.write('echo "All done"\n')
    scriptFile.close()
    
    #write geant 4 macro
    g4Macro = open('%s/g4steer.mac'%(outDir), 'w')
    g4Macro.write('/control/verbose 0\n')
    g4Macro.write('/control/saveHistory\n')
    g4Macro.write('/run/verbose 0\n')
    g4Macro.write('/event/verbose 0\n')
    g4Macro.write('/tracking/verbose 0\n')
    g4Macro.write('/N03/det/setField %1.1f T\n'%opt.Bfield)
    g4Macro.write('/N03/det/setModel %d\n'%opt.model)
    g4Macro.write('/random/setSeeds %d %d\n'%( random.uniform(0,100000), random.uniform(0,100000) ) )
    if opt.dogun :
        g4Macro.write('/generator/select particleGun\n')
        g4Macro.write('/gun/particle %s\n'%(opt.datatype))
        if opt.eta<5 : en=et*math.cosh(opt.eta)
        else : en=et
        g4Macro.write('/gun/energy %f GeV\n'%(en))
        if opt.model!=2 :
            alpha = 2*math.atan(math.exp(-1.*opt.eta));
            g4Macro.write('/gun/direction %f %f %f\n'%(math.cos(math.pi*opt.phi)*math.sin(alpha),math.sin(math.pi*opt.phi)*math.sin(alpha),math.cos(alpha)))
        #g4Macro.write('/gun/direction %f %f %f\n'%(math.cos(math.pi*opt.phi)*math.sin(opt.alpha),math.sin(math.pi*opt.phi)*math.sin(opt.alpha),math.cos(opt.alpha)))
        #g4Macro.write('/gun/direction %f %f %f\n'%(random.uniform(0,1000)/100.-5.,math.sin(opt.alpha),math.cos(opt.alpha)))
    else :
        g4Macro.write('/generator/select hepmcAscii\n')
        g4Macro.write('/generator/hepmcAscii/open %s\n'%(opt.datafile))
        g4Macro.write('/generator/hepmcAscii/verbose 0\n')
    g4Macro.write('/run/beamOn %d\n'%(nevents))
    g4Macro.close()
    
    #submit
    condorFile = open('%s/condorSubmitProd.sub'%(outDir), 'w')
    condorFile.write('universe = vanilla\n')
    condorFile.write('+JobFlavour = "nextweek"\n')
    condorFile.write('Executable = %s/runJob.sh\n'%outDir)
    condorFile.write('Output = %s/condorTree.out\n'%outDir)
    condorFile.write('Error = %s/condorTree.err\n'%outDir)
    condorFile.write('Log = %s/condorTree.log\n'%outDir)
    condorFile.write('Queue 1\n')
    condorFile.close()

    os.system('chmod u+rwx %s/runJob.sh'%outDir)
    if opt.nosubmit : os.system('echo condor_submit %s/condorSubmitProd.sub'%(outDir)) 
    else: os.system('condor_submit %s/condorSubmitProd.sub'%(outDir))

