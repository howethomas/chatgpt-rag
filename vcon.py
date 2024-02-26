import json

class Vcon:
    def __init__(self, dialog=None, parties=None, attachments=None, analysis=None, uuid=None, created_at=None, updated_at=None):
        self.dialog = dialog or []
        self.parties = parties or []
        self.attachments = attachments or []
        self.analysis = analysis or []
        self.uuid = uuid
        self.created_at = created_at
        self.updated_at = updated_at

    def add_dialog(self, dialog):
        self.dialog.append(dialog)

    def add_party(self, party):
        self.parties.append(party)

    def add_attachment(self, attachment):
        self.attachments.append(attachment)

    def add_analysis(self, analysis):
        self.analysis.append(analysis)

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "dialog": self.dialog,
            "parties": self.parties,
            "attachments": self.attachments,
            "analysis": self.analysis
        }

    @classmethod
    def from_dict(cls, vcon_dict):
        return cls(
            uuid=vcon_dict.get("uuid"),
            created_at=vcon_dict.get("created_at"),
            updated_at=vcon_dict.get("updated_at"),
            dialog=vcon_dict.get("dialog"),
            parties=vcon_dict.get("parties"),
            attachments=vcon_dict.get("attachments"),
            analysis=vcon_dict.get("analysis")
        )

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, vcon_json):
        vcon_dict = json.loads(vcon_json)
        return cls.from_dict(vcon_dict)

    def get_party_names(self):
        party_names = []
        for party in self.parties:
            if party.get("name"):
                party_names.append(party.get("name"))
            elif party.get("email"):
                party_names.append(party.get("email"))
            elif party.get("tel"):
                party_names.append(party.get("tel"))
        return party_names

    def get_agent_mailto(self):
        for party in self.parties:
            meta = party.get("meta")
            if not meta:
                return None
            role = meta.get("role")
            if role == "agent":
                return party.get("mailto")
            
    def get_customer_name(self):
        for party in self.parties:
            meta = party.get("meta")
            if not meta:
                return None
            role = meta.get("role")
            if role == "customer":
                best_name = party.get("name") or party.get("mailto") or party.get("tel")
                return best_name
            
    # Get the name of the dealer
    def get_dealer_name(self):
        # Dealer names are held in the dealer attachment
        for attachment in self.attachments:
            if attachment.get("type") == "strolid_dealer":
                info = json.loads(attachment.get("body"))
                return info.get("name")

    def get_team_id(self):
        # Dealer names are held in the dealer attachment
        for attachment in self.attachments:
            if attachment.get("type") == "strolid_dealer":
                info = json.loads(attachment.get("body"))
                team = info.get("team")
                return team.get("id")

    def get_team_name(self):
        # Dealer names are held in the dealer attachment
        for attachment in self.attachments:
            if attachment.get("type") == "strolid_dealer":
                info = json.loads(attachment.get("body"))
                team = info.get("team")
                return team.get("name")

    def get_dialog_urls(self):
        dialog_urls = []
        for dialog in self.dialog:
            if dialog.get("url"):
                dialog_urls.append(dialog.get("url"))
        return dialog_urls
    
    def get_summary(self):
        # Get the summary from the analysis, if it exists
        summary = None
        for analysis in self.analysis:
            if analysis.get("type") == "summary":
                summary = analysis.get("body")
            
        return f"""
        On {self.created_at}, there was a call involving {self.get_party_names()}.
        The uniuqe ID for this call is {self.get_uuid()}.
        The calls lasted {self.get_duration()} seconds, handled by {self.get_agent_mailto()}.
        The team was {self.get_team_name()}.
        You can listen to the call [here]({self.get_dialog_urls()}).

        {summary}
        """

    def get_created_at(self):
        return self.created_at

    def get_updated_at(self):
        return self.updated_at

    def get_uuid(self):
        return self.uuid
     
    def get_duration(self):
        duration = 0
        for dialog in self.dialog:
            duration += dialog.get("duration")
        return duration
    
    # TODO: Add a get_transcript() method
    def get_transcript(self):
        transcript = ""
        for dialog in self.dialog:
            if dialog.get("type", None) == "transcript":
                transcript += dialog.get("body")
        return transcript
    
    def __str__(self):
        return self.to_json()
    
    def __repr__(self):
        return self.to_json()
    
    def __eq__(self, other):
        return self.to_dict() == other.to_dict()
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        return hash(self.to_json())
    
    def __len__(self):
        return len(self.to_json())
    
    def __getitem__(self, key):
        return self.to_dict()[key]
    
    def __setitem__(self, key, value):
        self.to_dict()[key] = value

    def __delitem__(self, key):
        del self.to_dict()[key]

    def __iter__(self):
        return iter(self.to_dict())
    
        
