
# Google API imports
from oauth2client import client as oauth2_client
import httplib2
from apiclient import discovery as apiclient_discovery


# CONSTANTS
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_CONTENT_ID_API_SERVICE_NAME = "youtubePartner"
YOUTUBE_CONTENT_ID_API_VERSION = "v1"

CONTROL_STATUS_VALUES = ("preview","start","slate","noslate","cuepoint","stop")
BROADCAST_PART = "id,snippet,contentDetails,status"

# ERROR OBJECT
class Error(Exception):
	pass

# SERVICE OBJECT
class Service(object):
	def __init__(self,credentials):
		assert isinstance(credentials,oauth2_client.OAuth2Credentials)
		assert not credentials.invalid
		http = credentials.authorize(httplib2.Http())
		self.youtube = apiclient_discovery.build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,http=http)
		self.partner = apiclient_discovery.build(YOUTUBE_CONTENT_ID_API_SERVICE_NAME,YOUTUBE_CONTENT_ID_API_VERSION,http=http)

	def fetch_broadcasts(self,options):
		response = self.youtube.liveBroadcasts().list(
			broadcastStatus=options.get('status') or 'all',
			part=BROADCAST_PART,
			maxResults=options.get('max-results')
		).execute()
		return response.get("items",[])
	
	def fetch_broadcast(self,options):
		broadcast = options.get('broadcast')
		if not broadcast:
			raise Error("Missing broadcast")
		response = self.youtube.liveBroadcasts().list(
			id=broadcast,
			part=BROADCAST_PART
		).execute()
		return response.get("items",[])
	
	
	def fetch_streams(self,options):
		response = self.youtube.liveStreams().list(
			part="id,snippet,cdn,status",
			mine="true",
			maxResults=options.get('max-results')
		).execute()
		return response.get("items",[])

	def control_broadcast(self,options):
		broadcast = options.get('broadcast')
		status = options.get('status')
		if not broadcast:
			raise Error("Missing broadcast")
		if status not in CONTROL_STATUS_VALUES:
			raise Error("Missing or invalid status: should be one of %s" % ",".join(CONTROL_STATUS_VALUES))
		if status in ("slate"):
			return self.youtube.liveBroadcasts().control(
				id=broadcast,
				displaySlate=True,
				part=BROADCAST_PART
			).execute()
		if status in ("noslate"):
			return self.youtube.liveBroadcasts().control(
				id=broadcast,
				displaySlate=True,
				part=BROADCAST_PART
			).execute()
		return None


			



