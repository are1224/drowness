# 자료는 request와 response 의 개념 학습용으로만 사용하시고, 악용하지마세요 !!!
# 악용 시의 책임을 지지 않습니다..

import requests
import json

def get_url(url_text):
    # search_query = '갤럭시 노트 20'
    search_input = url_text
    search_query = search_input

    headers = {
        'x-youtube-client-name': '1',
        'x-youtube-client-version': '2.20200806.01.01'
    }

    video_headers = {
        'authority': 'www.youtube.com',
        'x-youtube-sts': '18484',
        'x-youtube-device': 'cbr=Chrome&cbrver=84.0.4147.105&ceng=WebKit&cengver=537.36&cos=Macintosh&cosver=10_15_5',
        'x-youtube-page-label': 'youtube.ytfe.desktop_20200805_1_RC1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
        'x-youtube-variants-checksum': 'a85f7843f63a8b7d2f0e800feae56a8e',
        'x-youtube-page-cl': '325146078',
        'x-spf-referer': 'https://www.youtube.com/results?search_query=%EA%B0%A4%EB%9F%AD%EC%8B%9C+%EB%85%B8%ED%8A%B8+20',
        'x-youtube-utc-offset': '540',
        'x-youtube-client-name': '1',
        'x-spf-previous': 'https://www.youtube.com/results?search_query=%EA%B0%A4%EB%9F%AD%EC%8B%9C+%EB%85%B8%ED%8A%B8+20',
        'x-youtube-client-version': '2.20200806.01.01',
        'dpr': '2',
        'x-youtube-time-zone': 'Asia/Seoul',
        'x-youtube-ad-signals': 'dt=1597134462858&flash=0&frm&u_tz=540&u_his=7&u_java&u_h=1050&u_w=1680&u_ah=1027&u_aw=1680&u_cd=30&u_nplug=3&u_nmime=4&bc=31&bih=948&biw=629&brdim=0%2C23%2C0%2C23%2C1680%2C23%2C1680%2C1027%2C644%2C948&vis=1&wgl=true&ca_type=image',
        'accept': '*/*',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.youtube.com/results?search_query=%EA%B0%A4%EB%9F%AD%EC%8B%9C+%EB%85%B8%ED%8A%B8+20',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': 'VISITOR_INFO1_LIVE=JBcPohHFkb8; GPS=1; YSC=uVMfLNJ5nV8; PREF=f4=4000000; ST-1gdf4lt=csn=e1cyX_POJZWU4wKH5ZKYAQ&itct=CIsBENwwGAEiEwil0Ym73pLrAhXTEVgKHcD9DGQyBnNlYXJjaFIT6rCk65-t7IucIOuFuO2KuCAyMJoBAxD0JA%3D%3D',
    }

    params = (
        ('search_query', search_query),
        ('pbj', '1'),
    )

    response = requests.get('https://www.youtube.com/results',
                            headers=headers, params=params)
    result = json.loads(response.text)

    contents = result[1]['response']['contents']['twoColumnSearchResultsRenderer']['primaryContents'][
        'sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']

    videoId = []

    for content in contents:
        keys = list(content.keys())

        if 'videoRenderer' in keys:
            videoId.append(content['videoRenderer']['videoId'])

    # 초반 과정 끝

    # 후반 과정
    # 영상의 id 값을 이용해서 광고 없는 영상 가져오기

    # 흔적
    # 0. 스크롤바가 가만히 있는데도 줄어든다 => request를 계속 보낸다.
    # 1. 같은 영상인데도 불구하고, 다른 광고가 뜬다.
        # - 광고영상과 컨텐츠 영상이 분리되어서, 저장되어 있다.
    # 2. 내가 광고영상과 컨텐츠 영상을 본다는 것은, 광고 영상과 컨텐츠 영상에 대한 각각의 요청을 보내서 각각의 응답을 받는 다는 뜻이다.
    # 3. 광고 영상을 안보는 프리미엄이라면 ?
        # 3-1 : "내가 프리미엄이니까 광고영상 주지마!" 라는 요청을 보내서 광고영상을 안보는 경우
        # 3-2 : "내가 프리미엄이니까 광고영상을 달라는 요청을 보내지마" -> 광고영상의 요청을 보내지 않아서 안보는 경우


    # 광고영상을 달라는 요청을 보내지 않는다면, 광고 영상을 보지 않을 수 있을 것이다.
        # 광고영상에 대한 요청과 컨텐츠 영상에 대한 요청이 다르다. -> 영상에 대한 요청이 뭘까?
            # 영상에 대한 요청이라는 것이 가지는 특징은 뭘까?
            # - 0번에 빗대어 생각해보면, 영상에 대한 요청은 영상을 범위별로 쪼개서 요청을 할 것이다. => range query로 범위를 조절(안보내면 풀로 온다)
            # - 영상에 대한 요청은 같은 곳에 요청을 보낼 것이다. 왜냐하면 영상은 한 곳에 저장되어 있기 때문이다. => RequestURL이 같을 것이다. => RequestURL 은 어떻게 알까? => 가장 먼저 보내는 요청에서 알아내야만 한다 !
            # - 영상을 쪼개서 달라는 요청을 보내기 때문에, 영상이 쪼개져서 날라오는 것


    # STEP 정리
    # 1. 영상 클릭
    # 2. 영상이 어디에 저장되어있는지(Request URL) 요청을 보내서 알아내기 **중요 !
    # 3. 2번에서 받은 응답의 Request URL로 요청을 보내서 영상 가져오기

    karaoke_vid_url = ''

    for vid in videoId:

        params = (
            ('v', vid),
            ('pbj', '1'),
        )

        response = requests.get('https://www.youtube.com/watch',
                                headers=video_headers, params=params)

        result = json.loads(response.text)

        player_response = result[2]['player']['args']['player_response']
        p_json = json.loads(player_response)

        streaming_data = p_json['streamingData']['formats']

        for f in streaming_data:
            keys = list(f.keys())

            if 'url' in keys:
                # print(f['url'])
                karaoke_vid_url = f['url']
                # print(karaoke_vid_url)
                return karaoke_vid_url
                # break
