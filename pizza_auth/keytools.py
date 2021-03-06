import eveapi
import json
import datetime

with open('config.json', 'r') as fh:
	config = json.loads(fh.read())

api = eveapi.EVEAPIConnection()

class KeyTools():
	def __init__(self, config):
		self.config = config["keytools"]
		self.authconfig = config
		self.bluealliances = self.getBlueAlliances()

	def getBlueAlliances(self):
		standingsapi = eveapi.EVEAPIConnection()
		auth = standingsapi.auth(keyID=self.config["executorkeyid"], vCode=self.config["executorkeyvcode"])
		standings = auth.corp.ContactList().allianceContactList
		standings = filter(lambda x:x.standing>self.config["alliancelimit"], standings)
		alliances = auth.eve.AllianceList().alliances
		alliances = map(lambda x:x.allianceID, alliances)
		bluealliances = {}
		for contact in standings:
			if contact.contactID in alliances:
				bluealliances[contact.contactID] = contact.contactName
		return bluealliances

	def getExpiry(self, character):
		accountstatusapi = eveapi.EVEAPIConnection()
		auth = accountstatusapi.auth(keyID=character.keyID, vCode=character.vCode)
		return datetime.datetime.fromtimestamp(auth.account.AccountStatus().paidUntil)

	def getCharacterStanding(self, character):
		if character.allianceName == self.authconfig["auth"]["alliance"]:
			return "PIZZA"
		elif character.allianceID in self.bluealliances:
			return "Ally"
		else:
			return "Ineligible"

	def getcharacters(self, keyid, vcode):
		auth = api.auth(keyID=keyid, vCode=vcode)
		characters = auth.account.Characters()
		results= []
		for character in characters.characters:
			sheet = auth.char.CharacterSheet(characterID=character.characterID)
			if hasattr(sheet, "allianceName"):
				character.allianceName = sheet.allianceName
			else:
				character.allianceName = ""
			if hasattr(sheet, "allianceID"):
				character.allianceID = sheet.allianceID
			else:
				character.allianceID = 0
			character.result = self.getCharacterStanding(character)
			results.append(character)
		return results

