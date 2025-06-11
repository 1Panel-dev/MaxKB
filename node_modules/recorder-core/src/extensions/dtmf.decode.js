/*
录音 Recorder扩展，DTMF（电话拨号按键信号）解码器，解码得到按键值
使用本扩展需要引入lib.fft.js支持

本扩展识别DTMF按键准确度高，误识别率低，支持识别120ms以上按键间隔+30ms以上的按键音，纯js实现易于移植

使用场景：电话录音软解，软电话实时提取DTMF按键信号等
https://github.com/xiangyuecn/Recorder
*/
(function(factory){
	var browser=typeof window=="object" && !!window.document;
	var win=browser?window:Object; //非浏览器环境，Recorder挂载在Object下面
	var rec=win.Recorder,ni=rec.i18n;
	factory(rec,ni,ni.$T,browser);
}(function(Recorder,i18n,$T,isBrowser){
"use strict";

/*
参数：
	pcmData:[Int16,...] pcm一维数组，原则上一次处理的数据量不要超过10秒，太长的数据应当分段延时处理
	sampleRate: 123 pcm的采样率
	prevChunk: null || {} 上次的返回值，用于连续识别
	
返回:
	chunk:{
		keys:[keyItem,...] 识别到的按键，如果未识别到数组长度为0
				keyItem:{
					key:"" //按键值 0-9 #*
					time:123 //所在的时间位置，ms
				}
		
		//以下用于下次接续识别
		lastIs:"" "":mute {}:match 结尾处是什么
		lastCheckCount:0 结尾如果是key，此时的检查次数
		prevIs:"" "":null {}:match 上次疑似检测到了什么
		totalLen:0 总采样数，相对4khz
		pcm:[Int16,...] 4khz pcm数据
		checkFactor:3 信号检查因子，取值1，2，3，默认为3不支持低于32ms的按键音检测，当需要检测时可以设为2，当信号更恶劣时设为1，这样将会减少检查的次数，导致错误识别率变高
		debug:false 是否开启调试日志
	}
*/
Recorder.DTMF_Decode=function(pcmData,sampleRate,prevChunk){
	prevChunk||(prevChunk={});
	var lastIs=prevChunk.lastIs||"";
	var lastCheckCount=prevChunk.lastCheckCount==null?99:prevChunk.lastCheckCount;
	var prevIs=prevChunk.prevIs||"";
	var totalLen=prevChunk.totalLen||0;
	var prevPcm=prevChunk.pcm;
	var checkFactor=prevChunk.checkFactor||0;
	var debug=prevChunk.debug;
	
	var keys=[];
	
	if(!Recorder.LibFFT){
		throw new Error($T.G("NeedImport-2",["DTMF_Decode","src/extensions/lib.fft.js"]));
	};
	var bufferSize=256;//小一点每次处理的时长不会太长，也不要太小影响分辨率
	var fft=Recorder.LibFFT(bufferSize);
	
	
	/****初始值计算****/
	var windowSize=bufferSize/4;//滑动窗口大小，取值为4的原因：64/4=16ms，16ms*(3-1)=32ms，保证3次取值判断有效性
	var checkCount=checkFactor||3;//只有3次连续窗口内计算结果相同判定为有效信号或间隔
	var muteCount=3;//两个信号间的最小间隔，3个窗口大小
	var startTotal=totalLen;
	
	/****将采样率降低到4khz，单次fft处理1000/(4000/256)=64ms，分辨率4000/256=15.625hz，允许连续dtmf信号间隔128ms****/
	var stepFloat=sampleRate/4000;
	
	var newSize=Math.floor(pcmData.length/stepFloat);
	totalLen+=newSize;
	var pos=0;
	if(prevPcm&&prevPcm.length>bufferSize){//接上上次的数据，继续滑动
		pos=windowSize*(checkCount+1);
		newSize+=pos;
		startTotal-=pos;
	};
	var arr=new Int16Array(newSize);
	if(pos){
		arr.set(prevPcm.subarray(prevPcm.length-pos));//接上上次的数据，继续滑动
	};
	
	for(var idxFloat=0;idxFloat<pcmData.length;pos++,idxFloat+=stepFloat){
		//简单抽样
		arr[pos]=pcmData[Math.round(idxFloat)];
	};
	pcmData=arr;
	sampleRate=4000;
	
	
	var freqStep=sampleRate/bufferSize;//分辨率
	var logMin=20;//粗略计算信号强度最小值，此值是先给0再根据下面的Math.log(fv)多次【测试】(下面一个log)出来的
	
	
	/****循环处理所有数据，识别出所有按键信号****/
	for(var i0=0; i0+bufferSize<=pcmData.length; i0+=windowSize){
		var arr=pcmData.subarray(i0,i0+bufferSize);
		var freqs=fft.transform(arr);
		var freqPs=[];
		
		var fv0=0,p0=0,v0=0,vi0=0, fv1=0,p1=0,v1=0,vi1=0;//查找高群和低群
		for(var i2=0;i2<freqs.length;i2++){
			var fv=freqs[i2];
			var p=Math.log(fv);//粗略计算信号强度
			freqPs.push(p);
			var v=(i2+1)*freqStep;
			if(p>logMin){
				if(fv>fv0 && v<1050){
					fv0=fv;
					p0=p;
					v0=v;
					vi0=i2;
				}else if(fv>fv1 && v>1050){
					fv1=fv;
					p1=p;
					v1=v;
					vi1=i2;
				};
			};
		};
		var pv0 =-1, pv1=-1;
		if(v0>600 && v1<1700 && Math.abs(p0-p1)<2.5){//高低频的幅度相差不能太大，此值是先给个大值再多次【测试】(下面一个log)得出来的
			//波形匹配度：两个峰值之间应当是深V型曲线，如果出现大幅杂波，可以直接排除掉
			var isV=1;
			//先找出谷底
			var pMin=p0,minI=0;
			for(var i2=vi0;i2<vi1;i2++){
				var v=freqPs[i2];
				if(v && v<pMin){//0不作数
					pMin=v;
					minI=i2;
				};
			};
			var xMax=(p0-pMin)*0.5//允许幅度变化最大值
			//V左侧，下降段
			var curMin=p0;
			for(var i2=vi0;isV&&i2<minI;i2++){
				var v=freqPs[i2];
				if(v<=curMin){
					curMin=v;
				}else if(v-curMin>xMax){
					isV=0;//下降段检测到过度上升
				};
			};
			//V右侧，上升段
			var curMax=pMin;
			for(var i2=minI;isV&&i2<vi1;i2++){
				var v=freqPs[i2];
				if(v>=curMax){
					curMax=v;
				}else if(curMax-v>xMax){
					isV=0;//上升段检测到过度下降
				};
			};
			
			if(isV){
				pv0=FindIndex(v0, DTMF_Freqs[0], freqStep);
				pv1=FindIndex(v1, DTMF_Freqs[1], freqStep);
			};
		};
		
		
		var key="";
		if (pv0 >= 0 && pv1 >= 0) {
			key = DTMF_Chars[pv0][pv1];
			if(debug)console.log(key,Math.round((startTotal+i0)/sampleRate*1000),p0.toFixed(2),p1.toFixed(2),Math.abs(p0-p1).toFixed(2)); //【测试】得出数值
			
			if(lastIs){
				if(lastIs.key==key){//有效，增加校验次数
					lastCheckCount++;
				}else{//异常数据，恢复间隔计数
					key="";
					lastCheckCount=lastIs.old+lastCheckCount;
				};
			}else{
				//没有连续的信号，检查是否在100ms内有检测到信号，当中间是断开的那种
				if(prevIs && prevIs.old2 && prevIs.key==key){
					if(startTotal+i0-prevIs.start<100*sampleRate/1000){
						lastIs=prevIs;
						lastCheckCount=prevIs.old2+1;
						if(debug)console.warn("接续了开叉的信号"+lastCheckCount);
					};
				};
				if(!lastIs){
					if(lastCheckCount>=muteCount){//间隔够了，开始按键识别计数
						lastIs={key:key,old:lastCheckCount,old2:lastCheckCount,start:startTotal+i0,pcms:[],use:0};
						lastCheckCount=1;
					}else{//上次识别以来间隔不够，重置间隔计数
						key="";
						lastCheckCount=0;
					};
				};
			};
		}else{
			if(lastIs){//下一个，恢复间隔计数
				lastIs.old2=lastCheckCount;
				lastCheckCount=lastIs.old+lastCheckCount;
			};
		};
		
		if(key){
			if(debug)lastIs.pcms.push(arr);
			//按键有效，并且未push过
			if(lastCheckCount>=checkCount && !lastIs.use){
				lastIs.use=1;
				keys.push({
					key:key
					,time:Math.round(lastIs.start/sampleRate*1000)
				});
			};
			//重置间隔数据
			if(lastIs.use){
				if(debug)console.log(key+"有效按键",lastIs);
				lastIs.old=0;
				lastIs.old2=0;
				lastCheckCount=0;
			};
		}else{
			//未发现按键
			if(lastIs){
				if(debug)console.log(lastIs) //测试，输出疑似key
				prevIs=lastIs;
			};
			lastIs="";
			lastCheckCount++;
		};
	};
	
	return {
		keys:keys
		
		,lastIs:lastIs
		,lastCheckCount:lastCheckCount
		,prevIs:prevIs
		,totalLen:totalLen
		,pcm:pcmData
		,checkFactor:checkFactor
		,debug:debug
	};
};



var DTMF_Freqs = [
	[697, 770, 852, 941],
	[1209, 1336, 1477, 1633]
];
var DTMF_Chars = [
	["1", "2", "3", "A"],
	["4", "5", "6", "B"],
	["7", "8", "9", "C"],
	["*", "0", "#", "D"],
];
var FindIndex=function(freq, freqs, freqStep){
	var idx=-1,idxb=1000;
	for(var i=0;i<freqs.length;i++){
		var xb=Math.abs(freqs[i]-freq);
		if(idxb>xb){
			idxb=xb;
			if(xb<freqStep*2){//最多2个分辨率内误差
				idx=i;
			};
		};
	};
	return idx;
};
	
}));