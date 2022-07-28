import requests
import json
import asyncio
import aiohttp

# async def main():
# 	async with aiohttp.ClientSession() as session:
# 		async with session.get('https://api.trakt.tv/calendars/my/movies/start_date/days',
# 			headers={'trakt-api-key':'2992373b3dfa4124bd64269820130237952fdec58395067fe15955007f53cf36', 'Content-Type':'application/json', 'trakt-api-version':'2'},
# 			json={'title':'Try Bearer'}) as resp:

# 			response = await resp.json()
# 			print(response)

# asyncio.run(main())
def main():


     headers = {'Content-Type': 'application/json'}
     values= {'client_id':'2992373b3dfa4124bd64269820130237952fdec58395067fe15955007f53cf36'}
    # payload = {'response_type':'code', 'client_id':'2992373b3dfa4124bd64269820130237952fdec58395067fe15955007f53cf36', 'redirect_uri':'urn:ietf:wg:oauth:2.0:oob' }
    response = requests.post('https://api.trakt.tv/oauth/device/code', data=values, headers=headers)
    # response = requests.get('https://trakt.tv/oauth/authorize', params=payload, headers=headers)
    print(response)
    print(response.text)
    print(response.json())



    # m_headers = {
    #     'Content-Type': 'application/json',
    #     'Authorization': '531503ab053fe2d89caa12d8132b352d3f2a4047b05b4a8b0a296aebfced1a6c',
    #     'trakt-api-version': '2',
    #     'trakt-api-key': '2992373b3dfa4124bd64269820130237952fdec58395067fe15955007f53cf36'
    #     }
    # request = requests.get('https://api.trakt.tv/calendars/my/movies/start_date/days', headers=m_headers)

    # print(request)

if __name__ == "__main__":
    main()