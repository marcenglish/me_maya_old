import maya.cmds as m
class Limb():
    def setupObj(self,joints,name,ik,ikFollow,rotAxis,switchDefault,ikHandleOrient,branchConnections,splitIK_ratio):
        print "setting up "+name
        self.name = name        
        if len(joints) == 0:
            print "class created, no attributes assigned"
        else:
            self.joints = joints        
            self.startPlugs = {'IN':'base_'+joints[0]}
            self.endPlugs = {'IN':'base_'+joints[-1],'OUT':'base_'+joints[-1]}
            self.ikFollow = ikFollow
            self.switch = 'self'
            self.specialLabel = ''        
            self.ik = ik            
            self.ctrls = ik #squash method requires 'ctrls' attr.  to be fixed.
            self.switchDefault = switchDefault
            self.ikHO_Base = ikHandleOrient
            self.branchConnections = branchConnections
            tempData = rotAxis.split('-')
            self.rotAxis = tempData[0]
            self.rotDir = 1

            if len(tempData) > 1:                
                self.rotDir = -1
            if splitIK_ratio != '':
                self.driverA_POS = splitIK_ratio[0]    
                self.driverB_POS = splitIK_ratio[1]    
    def assignDetails(self,side,roll):
                self.side = side
                self.sJoints = []
                for ea in self.joints:
                    self.sJoints.append(ea+side)                
                if self.ikHO_Base == '':            
                    self.ikHandleOrienter = self.ikHO_Base
                else:
                    self.ikHandleOrienter = self.ikHO_Base+side    
                self.pvPositionOffset = m.getAttr('base_'+self.joints[1]+side+".tx")*8*self.rotDir
                self.twigConnections = ['plug_start_IN_->_FK_'+self.joints[0]+side+'_Space_$_parentConstraint_$_True',
                                        'plug_start_IN_->_IK_'+self.joints[0]+side+'_Space_$_parentConstraint_$_True',
                                        'plug_start_IN_->_Rig_'+self.joints[0]+side+'_Space_$_parentConstraint_$_True',
                                        'plug_start_IN_->_'+self.joints[0]+side+'_FK_Space_$_parentConstraint_$_True',
                                        'plug_start_IN_->_'+self.joints[0]+side+'_bendyTwist_start_$_parentConstraint_$_False']            
                self.lengths= []
                for i in range(len(self.joints)-1):
                    self.lengths.append(abs(m.getAttr('base_'+self.joints[i+1]+side+'.tx')))
                                     
                self.ctrlParent = self.name+side+'_Controls'
                self.roll = roll
                self.defIkFollow = self.name+side+'_plug_start_IN'
                if self.ikFollow != "":
                    self.defIkFollow = self.ikFollow
                
class trunk():
    def __init__(self,joints,name,ik,ctrls,fkDiv,branchConnections):        
        self.name = name
        self.side = ''
        self.fkDiv = fkDiv
        fkControllers = ['low','med','high']
        self.defIkFollow=[name+'_FK_'+fkControllers[fkDiv-1],ctrls[-1],ctrls[-1]+'_IK','WorldOffset']
        if len(joints) == 0:
            print "class created, no attributes assigned"
        else:
            self.joints = joints
        self.ik = ik
        self.ctrls = ctrls
        self.startPlugs = {'IN':'base_'+joints[0],'OUT':'base_'+joints[0]}
        self.endPlugs = {'OUT':'base_'+joints[-1]}
        self.branchConnections = branchConnections
        self.twigConnections = ['plug_end_OUT_<-_'+ctrls[1]+'_id_$_parentConstraint_$_True',
                                'plug_end_OUT_->_'+name+'_twistEnd_$_parentConstraint_$_False',
                                'plug_start_OUT_<-_'+ctrls[0]+'_$_parentConstraint_$_True',
                                'plug_start_IN_->_'+ctrls[2]+'_Space_$_parentConstraint_$_True',                                
                                ]
class Extremety():
    def setupObj(self,joints,name,auxName,parentObj):
        self.name = name
        self.auxName = auxName
        self.side = ''
        self.endPlugs = []
        if len(joints) == 0:
            print "class created, no attributes assigned"
        else:
            self.joints = joints           
        


        self.startPlugs = {'IN':'base_'+parentObj.joints[-1],'OUT':'base_'+parentObj.joints[-1]}
        self.parent = parentObj
    def assignDetails(self,side):
                self.side = side        
                self.switch = self.parent.ik+side+'_SW'
                self.branchConnections = [self.parent.name+side+'_plug_end_OUT_->_'+self.name+side+'_plug_start_IN']
                self.sJoints = []
                for ea in self.joints:
                    self.sJoints.append(ea+side)


def createObjSet(type):   
    if type == "biped":
        Arm.setupObj(['shoulder','elbow','wrist'],'Arm','hand',['Hip','WorldOffset','Chest_IK'],'-Y',0,'base_wrist',['Spine_plug_end_OUT_->_Arm_id_plug_start_IN'],'')
        Leg.setupObj(['hip','knee','ankle'],'Leg','foot',['Hip','WorldOffset'],'Y',1,'',['Spine_plug_start_OUT_->_Leg_id_plug_start_IN'],'')
        ###############################################################
        Hand.setupObj(['iterated'],'Hand','Hand',Arm)
        Hand.twigConnections = ['plug_start_IN_->_pinky_id_GRP_$_parentConstraint_$_True',
                                'plug_start_IN_->_ring_id_GRP_$_parentConstraint_$_True',
                                'plug_start_IN_->_middle_id_GRP_$_parentConstraint_$_True',
                                'plug_start_IN_->_index_id_GRP_$_parentConstraint_$_True',
                                'plug_start_IN_->_thumb_id_GRP_$_parentConstraint_$_True',]
        ###############################################################
        Foot.setupObj(['heel','ball','toe'],'Foot','foot',Leg)        
        Foot.spaces = ("ankle:ankle","heel%_Space:heel","heel:heel","toe%_Space:toe","ballPivot:ball","toePivot:toe","toe:toe","ball:ball")
        Foot.twigConnections = ['plug_start_OUT_<-_foot_ball_id_$_parentConstraint_$_True']
        Foot.attrs = {'heelPivot':'INV_IK_heel_id_.rotateZ' ,
                      'ballPivot':'INV_IK_ballPivot_id_.rotateZ',
                      'toePivot':'INV_IK_toePivot_id_.rotateZ',
                      'footRoll':'FootINV_IK_id__CLMP.inputR',
                      'ballRoll':'INV_IK_ballPivot_id_.rotateY' ,
                      'toeRoll':'INV_IK_toe_id_.rotateY',
                      'tilt':'INV_IK_heel_id_.rotateX'}

        Clavicle.setupObj(['clavicle','shoulder'],'Clavicle','','','','','',['Spine_plug_end_OUT_->_Clavicle_id_plug_start_IN'],'')
        Clavicle.branchConnections = ['Clavicle_id_plug_end_OUT_->_Arm_id_plug_start_IN']
        Clavicle.twigConnections = ['plug_end_OUT_<-_Clav_IK_shoulder_id_$_parentConstraint_$_False',                            
                                    'plug_start_IN_->_Clavicle_id_FK_Space_$_parentConstraint_$_False']
    
    
    if type == "quad":
        Arm.setupObj(['shoulder','elbow','forearm','wrist'],'Frontleg','frontFoot','Hip','-Y',1,'base_wrist',['Spine_plug_end_OUT_->_Frontleg_id_plug_start_IN'],[0.45,0.55])
        Leg.setupObj(['hip','knee','hock','ankle'],'Leg','foot','Hip','Y',1,'',['Spine_plug_start_OUT_->_Leg_id_plug_start_IN'],[0.47,0.53])    
        ###############################################################
        Foot.setupObj(['heel','ball','toe'],'Foot','foot',Leg)
        Foot.spaces = ("ankle:ankle","heel%_Space:heel","heel:heel","toe%_Space:toe","ballPivot:ball","toe:toe","ball:ball")
        Foot.twigConnections = ['plug_start_OUT_<-_foot_ball_id_$_parentConstraint_$_True']
        Foot.attrs = {'heelPivot':'INV_IK_heel_id_.rotateZ' ,
                      'ballPivot':'INV_IK_ballPivot_id_.rotateZ',
                      'toePivot':'INV_IK_toe_id_.rotateZ',
                      'footRoll':'FootINV_IK_id__CLMP.inputR',
                      'ballRoll':'INV_IK_ballPivot_id_.rotateY' ,
                      'toeRoll':'INV_IK_toe_id_.rotateY'}       
        
        FrontFoot.setupObj(['fHeel','fBall','fToe'],'FrontFoot','frontFoot',Arm)
        FrontFoot.spaces = ("wrist:wrist","fHeel%_Space:fHeel","fHeel:fHeel","fToe%_Space:fToe","fBallPivot:fBall","fToe:fToe","fBall:fBall")
        FrontFoot.twigConnections = ['plug_start_OUT_<-_foot_fBall_id_$_parentConstraint_$_True']
        FrontFoot.attrs = {'heelPivot':'INV_IK_fHeel_id_.rotateZ' ,
                      'ballPivot':'INV_IK_fBallPivot_id_.rotateZ',
                      'toePivot':'INV_IK_fToe_id_.rotateZ',
                      'footRoll':'FrontFootINV_IK_id__CLMP.inputR',
                      'ballRoll':'INV_IK_fBallPivot_id_.rotateY' ,
                      'toeRoll':'INV_IK_fToe_id_.rotateY'} 



Clavicle = Limb()
Arm = Limb()
Leg = Limb()
Frontleg = Limb()
Hand = Extremety()
Foot = Extremety()
FrontFoot = Extremety()

###############################################################
###############################################################
Spine = trunk(  ['pelvis','spine_0','spine_1','spine_2','spine_3','spine_4','spine_5'], #joints
                'Spine', #name
                'Chest', #ikHandle
                ['Hip_IK','Chest_IK','Hip'], #CtrlNames
                3, #FkDivisions
                ['WorldOffset_->_Spine_plug_start_IN'], #Branch connections
                )
###############################################################
###############################################################
Neck = trunk(   ['neck_0','neck_1','neck_2','head_0'],
                'Neck',
                'Head',
                ['Neck_IK','Head_IK','Neck'],
                1,
                ['Spine_plug_end_OUT_->_Neck_plug_start_IN'])
###############################################################
###############################################################



print "----CLASSES LOADED---"