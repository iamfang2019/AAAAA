import {
    Crypto, load, _
}
from 'assets://js/lib/cat.js';

let key = '厂子资源';
let HOST = '';
let siteKey = '';
let siteType = 0;
const cookie = {};



const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1';

async function request(reqUrl, referer, mth, data, hd) {
    const headers = {
        'User-Agent': UA,
        Cookie: _.map(cookie, (value, key) => {
            return `${key}=${value}`;
        }).join(';'),
    };
    if (referer) headers.referer = encodeURIComponent(referer);
    let res = await req(reqUrl, {
        method: mth || 'get',
        headers: headers,
        data: data,
        postType: mth === 'post' ? 'form' : '',
    });
    if (res.headers['set-cookie']) {
        const set_cookie = _.isArray(res.headers['set-cookie']) ? res.headers['set-cookie'].join(';') : res.headers['set-cookie'];
        const cks = set_cookie.split(';');
        for (const c of cks) {
            const tmp = c.trim();
            if (tmp.startsWith('result=')) {
                cookie.result = tmp.substring(7);
                return await request(reqUrl, reqUrl, 'post', {
                    result: cookie.result,
                });
            } else if (tmp.startsWith('esc_search_captcha=1')) {
                cookie.esc_search_captcha = 1;
                delete cookie.result;
                return await request(reqUrl);
            }
        }
        // console.log(res.headers['set-cookie']);
    }
    return res.content;
}

// cfg = {skey: siteKey, ext: extend}
async function init(cfg) {
	try{
		siteKey = cfg.skey;
		siteType = cfg.stype;
		let html = await request('https://cz01.vip');
		let matches = html.matchAll(/推荐访问<a href="(.*)"/g);
		for (let match of matches) {
		    try {
		        let rcmdUrl = match[1];
		        let res = await req(rcmdUrl, {
		            method: 'get',
		            headers: {
		                'User-Agent': UA,
		            },
		            redirect: 0,
		        });
		        let location = res.headers['location'];
                console.debug("-" + rcmdUrl + ">>" + location);
		        if (!_.isEmpty(location)) {
		            HOST = location;
		        } else {
		            HOST = rcmdUrl;
		            break;
		        }
		    } catch(e) {
		    }
		}
		return {};
	}catch(e){
		//TODO handle the exception
		console.debug("---" + e);
	}
}

async function home(filter) {
	let filterObj = {};
	const html = await request(HOST + '/movie_bt');
	const $ = load(html);
	const sortName = ['电影', '电视剧', '国产剧', '美剧', '韩剧', '日剧', '海外剧', '动画'];
	const series = $('div#beautiful-taxonomy-filters-tax-movie_bt_series > a[cat-url*=movie_bt_series]');
	let classes = _.map(series, (s) => {
		if(sortName.indexOf(s.children[0].data) < 0) return{};
		let typeId = s.attribs['cat-url'];
		typeId = typeId.substring(typeId.lastIndexOf('/') + 1);
		return {
			type_id: typeId,
			type_name: s.children[0].data,
		};
	});
	
	classes = _.sortBy(classes, (c) => {
		const index = sortName.indexOf(c.type_name);
		return index === -1 ? sortName.length : index;
	});
	return ({
		class: classes,
		filters: filterObj,
	});
}

async function homeVod() {}

async function category(tid, pg, filter, extend) {
	if(pg <= 0) pg = 1;
    const link = HOST + '/movie_bt/movie_bt_series/' + tid + (pg > 1 ? `/page/` + pg : '');
    const html = await request(link);
    const $ = load(html);
    const items = $('div.mrb > ul > li');
    let videos = _.map(items, (item) => {
        const img = $(item).find('img:first')[0];
        const a = $(item).find('a:first')[0];
        const hdinfo = $($(item).find('div.hdinfo')[0]).text().trim();
        const jidi = $($(item).find('div.jidi')[0]).text().trim();
        return {
            vod_id: a.attribs.href.replace(/.*?\/movie\/(.*).html/g, '$1'),
            vod_name: img.attribs.alt,
            vod_pic: img.attribs['data-original'],
            vod_remarks: jidi || hdinfo || '',
        };
    });
    return ({
        page: parseInt(pg),
        pagecount: 0,
        limit: 0,
        total: 0,
        list: videos,
    });
}


function stripHtmlTag(src) {
    return src
        .replace(/<\/?[^>]+(>|$)/g, '')
        .replace(/&.{1,5};/g, '')
        .replace(/\s{2,}/g, ' ');
}


async function detail(id) {
	const html = await request(HOST + '/movie/' + id + '.html');
	const $ = load(html);
	const detail = $('ul.moviedteail_list > li');
	let vod = {
		vod_id: id,
		vod_pic: $('div.dyimg img:first').attr('src'),
		vod_remarks: '',
		vod_content: '[关注公众号:影视资源站] ' + stripHtmlTag($('div.yp_context').html()).trim(),
	};
	for (const info of detail) {
		const i = $(info).text().trim();
		if (i.startsWith('地区：')) {
			vod.vod_area = i.substring(3);
		} else if (i.startsWith('年份：')) {
			vod.vod_year = i.substring(3);
		} else if (i.startsWith('导演：')) {
			vod.vod_director = _.map($(info).find('a'), (a) => {
				return a.children[0].data;
			}).join('/');
		} else if (i.startsWith('主演：')) {
			vod.vod_actor = _.map($(info).find('a'), (a) => {
				return a.children[0].data;
			}).join('/');
		} else if (i.startsWith('语言：')) {
			vod.vod_lang = i.substring(3);
		}
	}
	const playlist = _.map($('div.paly_list_btn > a'), (a) => {
		return a.children[0].data + '$' + a.attribs.href.replace(/.*?\/v_play\/(.*).html/g, '$1');
	});
	vod.vod_play_from = key;
	vod.vod_play_url = playlist.join('#');
    return JSON.stringify({
        list: [vod],
    });
}

function extractRootDomain(url) {
    // 使用正则表达式匹配协议和根域名
    var match = url.match(/^https?:\/\/([^\/?#]+)(?:[\/?#]|$)/i);
    return match && match[0]; // 返回匹配到的结果
}

async function play(flag, id, flags) {
	try{
		const link = HOST + '/v_play/' + id + '.html';
		const html = await request(link);
		const $ = load(html);
		const iframe = $('.videoplay iframe');
        let playHost = "";
		if (iframe.length > 0) {
		    const rUrl = iframe[0].attribs.src;
            playHost = extractRootDomain(rUrl);
		    // 请求
		    const iframeHtml = (
		        await req(rUrl, {
		            headers: {
		                Referer: link,
		                'User-Agent': UA,
		            },
		        })
		    ).content;
            console.debug("iframeHtml"+iframeHtml);
		    const rand = iframeHtml.match(/var rand = "(.*?)"/); // .split('').reverse().join('');
		    const encrypted = iframeHtml.match(/var player = "(.*?)"/); // .split('').reverse().join('');
		    if (!_.isEmpty(rand) && !_.isEmpty(encrypted)){
		        const key = Crypto.enc.Utf8.parse('VFBTzdujpR9FWBhe');
		        const iv = Crypto.enc.Utf8.parse(rand);
		        const decrypted = decryptPlayer(encrypted[1], 'VFBTzdujpR9FWBhe', rand[1]);
		        const list = JSON.parse(decrypted);
                let playUrl = list.url;
                if(!playUrl.startsWith("http")) playUrl = playHost + playUrl;
                console.debug(list + "\r\n" + playUrl);
		        return JSON.stringify({
					parse: 0,
					url: playUrl,
					header: {
						'User-Agent': UA,
					},
				});
		    } else {
		        const resultv2Match = iframeHtml.match(/var result_v2 = {(.*?)};/);
		        if (!_.isEmpty(resultv2Match)) {
		            const resultv2 = JSON.parse('{' + resultv2Match[1] + '}');
		            const playUrl = decryptResultV2(resultv2.data);
		            return JSON.stringify({
						parse: 0,
						url: playUrl,
						header: {
							'User-Agent': UA,
						},
					});
		        } else {
		            return JSON.stringify({
						parse: 0,
						url: rUrl,
						header: {
							'User-Agent': UA,
						},
					});
		        }
		    }
		} else {
		    const js = $('script:contains(window.wp_nonce)').html();
		    const group = js.match(/(var.*)eval\((\w*\(\w*\))\)/);
		    const md5 = Crypto;
		    const result = eval(group[1] + group[2]);
		    const playUrl = result.match(/url:.*?['"](.*?)['"]/)[1];
		    return JSON.stringify({
						parse: 0,
						url: playUrl,
						header: {
							'User-Agent': UA,
						},
					});
		}
	}catch(e){
		//TODO handle the exception
		console.debug("yyy:" + e);
	}
}


function decryptPlayer(text, key, iv) {
    const keyData = Crypto.enc.Utf8.parse(key || 'PBfAUnTdMjNDe6pL');
    const ivData = Crypto.enc.Utf8.parse(iv || 'sENS6bVbwSfvnXrj');
    const content = Crypto.AES.decrypt(text, keyData, {
        iv: ivData,
        padding: Crypto.pad.Pkcs7
    }).toString(Crypto.enc.Utf8);
    return content;
}

function decryptResultV2(text) {
    const data = text.split('').reverse().join('');
    const hexData = Crypto.enc.Hex.parse(data);
    const decoded = hexData.toString(Crypto.enc.Utf8);
    const pos = (decoded.length - 7) / 2;
    const firstPart = decoded.substring(0, pos);
    const secondPart = decoded.substring(pos + 7);
    return firstPart + secondPart;
}

async function search(wd, quick) {
	let videos = [];
    return JSON.stringify({
        list: videos,
    });
}

export function __jsEvalReturn() {
    return {
        init: init,
        home: home,
        homeVod: homeVod,
        category: category,
        detail: detail,
        play: play,
        search: search,
    };
}