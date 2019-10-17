# -*- coding: utf-8 -*-
from tools import Crypter
import requests
import json
import base64
import time
import random
import sys
import inspect
from collections import OrderedDict

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class API(object):
	def __init__(self):
		self.s=requests.session()
		self.s.verify=False
		if 'win' in sys.platform:
			self.s.proxies.update({'http': 'http://127.0.0.1:8888','https': 'https://127.0.0.1:8888',})
		self.debug=True
		self.c=Crypter()
		self.api_url='https://nrbna.channel.or.jp'
		self.teams=None
		self.platform=1#1 android 2 other
		self.app_version='2.0.3'
		self.main_revision=0
		self.assetbundle_revision=0
		self.uuid=self.getRNDId().upper()
		self.ad_id=self.getRNDId()
		self.platform_user_id=self.getRNDPlatform()
		self.player_id=0
		self.ssid=None
		self.app_auth_key='7SkWC2nhKPVdIgzLgC17zIVI2qx0vPhO'
		self.region=2

	def whoami(self): 
		return inspect.stack()[1][3]
	
	def log(self,msg):
		if self.debug:
			print '[%s]%s'%(time.strftime('%H:%M:%S'),msg.encode('utf-8'))
	
	def genRandomHex(self,n):
		return ''.join([random.choice('0123456789ABCDEF') for x in range(n)]).lower()

	def getRNDPlatform(self):
		return self.genRandomHex(16)

	def getRNDId(self):
		return '%s-%s-%s-%s-%s'%(self.genRandomHex(8),self.genRandomHex(4),self.genRandomHex(4),self.genRandomHex(4),self.genRandomHex(12))

	def buildBase(self):
		_base={}
		_base['platform']=self.platform
		_base['platform_version']="Android OS 7.0 / API-24 (NRD90R/3141966)"
		_base['model']="htc Nexus 9"
		_base['sim']=0
		_base['uuid']=self.uuid
		_base['platform_user_id']=self.platform_user_id
		_base['ad_id']=self.ad_id
		_base['request_id']=int(time.time())
		_base['app_version']=self.app_version
		_base['app_auth_key']=self.app_auth_key
		_base['main_revision']=self.main_revision
		_base['assetbundle_revision']=self.assetbundle_revision
		_base['region']=self.region
		_base['app_package_id']=self.region
		_base['timezone']="CET 02:00:00"
		_base['country']="FR"
		_base['currency']="USD"
		_base['language']="en"
		_base['player_id']=self.player_id
		_base['ssid']=self.ssid
		return _base

	def callAPI(self,_data,path,repeat=False):
		_head=self.makeHeaders(str(_data['request_id']) if not repeat else str(int(time.time())))
		r=self.s.post(self.api_url+path,data=self.c.encode(json.dumps(_data)),headers=_head,stream=True)
		_chunks=''
		for chunk in r.iter_content(chunk_size=1024): 
			if chunk:
				_chunks=_chunks+chunk
		_res= "".join([self.c.decode(_chunks).rsplit("}" , 1)[0] , "}"])
		try:
			_res_json=json.loads(_res)
		except:
			self.log('have some error in callAPI')
			return self.callAPI(_data,path,True)
		if 'player_id' in _res and self.player_id==0:
			self.setPlayerId(_res_json)
		if 'u_chara_team_mission' in _res:
			self.setTeams(_res_json)
		if 'ssid' in _res:
			self.setSsid(_res_json['ssid'])
		return _res

	def setTeams(self,id):
		self.teams=id['u_chara_team_mission']
		
	def setPlayerId(self,id):
		self.player_id=id['player_id']
		
	def setSsid(self,id):
		self.ssid=id
		
	def makeHeaders(self,a1):
		return OrderedDict([('X-Uuid',self.uuid),('X-Ad-Id',self.ad_id),('X-Player-Id',str(self.player_id)),('X-Platform',str(self.platform)),('X-Language','en'),('X-App-Version',self.app_version),('X-Model','htc Nexus 9'),('X-Platform-Version','Android OS 7.0 / API-24 (NRD90R/3141966)'),('X-Currency','USD'),('X-Platform-User-Id',self.platform_user_id),('X-Request-Id',a1),('X-Sim','0'),('X-Unity-Version','5.3.4p6'),('X-Country','FR'),('X-App-Auth-Key',self.app_auth_key),('Content-Type','text/plain'),('X-Assetbundle-Revision',str(self.assetbundle_revision)),('X-Region',str(self.region)),('X-App-Package-Id',str(self.region)),('X-Timezone','CET 02:00:00'),('X-Main-Revision',str(self.main_revision)),('User-Agent','Dalvik/2.1.0 (Linux; U; Android 7.0; Nexus 9 Build/NRD90R)')])

	def parseRevisions(self,data):
		res=json.loads(data)
		self.assetbundle_revision=res['assetbundle_revision']
		self.main_revision=res['main_revision']
		
	def doStartup(self):		
		_base=self.buildBase()
		_base['hkey']=1
		res= self.callAPI(_base,'/api/base/startup.json')
		self.parseRevisions(res)
		return res
		
	def doRegister(self,username):
		_base=self.buildBase()
		_base['player_name']=username
		return self.callAPI(_base,'/api/player/regist.json')
		
	def doAuth(self):
		_base=self.buildBase()
		return self.callAPI(_base,'/api/base/auth.json')
	
	def getPlayer(self):
		_base=self.buildBase()
		tmp= self.callAPI(_base,'/api/base/player.json')
		_res_json=json.loads(tmp)
		self.log('public_id:%s username:%s'%(_res_json['public_id'],_res_json['player_name']))
		return tmp
	
	def getMail(self):
		_base=self.buildBase()
		return self.callAPI(_base,'/api/base/mail.json')
		
	def getAchievement(self):
		_base=self.buildBase()
		return self.callAPI(_base,'/api/achievement/list.json')

	def getTransferCode(self):
		_base=self.buildBase()
		tmp= self.callAPI(_base,'/api/transfer/publish.json')
		self.log('transfer code:%s'%(json.loads(tmp)['transfer_code']))
		return tmp
		
	def setTutorial(self,id):
		_base=self.buildBase()
		_base['tutorial_id']=id
		return self.callAPI(_base,'/api/player/tutorial.json')

	def getSupporter(self):
		_base=self.buildBase()
		return self.callAPI(_base,'/api/mission/supportlist.json')
		
	def doStartSolo(self,mission_id,player_id,chara_id,chara_level,skill_level,ability_count,support_luck,fp):
		_base=self.buildBase()
		_base['mission_id']=mission_id
		_base['camp_mission_ids']=[]
		_base['support_player_id']=player_id
		_base['support_chara_id']=chara_id
		_base['support_chara_level']=chara_level
		_base['support_skill_level']=skill_level
		_base['support_ability_count']=ability_count
		_base['support_luck']=support_luck
		_base['add_friend_point']=fp
		return self.callAPI(_base,'/api/mission/startsolo.json')

	def doResultSolo(self,hash,ids,coin):
		_base=self.buildBase()
		_base['hash']=hash
		_base['mission_sub_id_list']=ids
		_base['get_coin']=coin
		_base['exclude_drop_units']=[]
		_base['exclude_drop_gems']=[]
		return self.callAPI(_base,'/api/mission/resultsolo.json') 
		
	def completeMission(self,mission_id,player_id,chara_id,chara_level,skill_level,ability_count,support_luck,fp):
		supporter=self.getSupporter()
		res=self.doStartSolo(mission_id,player_id,chara_id,chara_level,skill_level,ability_count,support_luck,fp)
		res_js=json.loads(res)
		_hash=res_js['hash']
		return self.doResultSolo(_hash,[1,2,3],100)
		
	def doTransfer(self,public_id,code):
		_base=self.buildBase()
		_base['public_id']=public_id
		_base['transfer_code']=code
		return self.callAPI(_base,'/api/transfer/input.json')
		
	def doTeammission(self):
		_base=self.buildBase()
		_base['u_chara_team_mission']=self.teams
		return self.callAPI(_base,'/api/chara/teammission.json')
		
	def getBoxList(self):
		_base=self.buildBase()
		return self.callAPI(_base,'/api/box/list.json')
		
	def getBoxes(self,ids):
		_base=self.buildBase()
		_base['box_no_list']=ids
		return self.callAPI(_base,'/api/box/get.json')
		
	def changeTeams(self,team_num,mem,id):
		for i in self.teams:
			if self.teams[i]['team_no']==team_num:
				self.teams[i]['member%s_chara_no'%(mem)]=id
				break
		self.doTeammission()
		
	def makeNewAccount(self):
		self.doStartup()
		self.doAuth()
		self.doRegister('Mila432')
		self.doAuth()
		self.getPlayer()
		self.getMail()
		self.getAchievement()
		self.getTransferCode()
		_first_reward=json.loads(self.completeMission(100001,0,10496,1,1,0,2,50))
		print self.setTutorial(1)
		for i in _first_reward['item_save_info']['u_chara']:
			self.changeTeams(1,5,i)
		print self.setTutorial(2)
		#self.completeMission(100002,0,10023,1,1,0,2,50)
		print self.setTutorial(3)
		boxes=json.loads(self.getBoxList())['u_box']
		tmp=[]
		for i in boxes:
			tmp.append(i)
		self.getBoxes(tmp)
		print self.setTutorial(4)
		print self.setTutorial(5)
		print self.setTutorial(6)
		print self.setTutorial(7)
		self.getTransferCode()
		
if __name__ == "__main__":
	a=API()
	a.makeNewAccount()