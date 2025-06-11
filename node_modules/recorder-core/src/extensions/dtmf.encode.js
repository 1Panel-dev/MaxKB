/*
录音 Recorder扩展，DTMF（电话拨号按键信号）编码生成器，生成按键对应的音频PCM信号

本扩展分两个功能：
	DTMF_Encode
	DTMF_EncodeMix

本扩展生成信号代码、原理简单粗暴，纯js实现易于移植，0依赖

使用场景：DTMF按键信号生成，软电话实时发送DTMF按键信号等
https://github.com/xiangyuecn/Recorder
*/
(function(factory){
	var browser=typeof window=="object" && !!window.document;
	var win=browser?window:Object; //非浏览器环境，Recorder挂载在Object下面
	var rec=win.Recorder,ni=rec.i18n;
	factory(rec,ni,ni.$T,browser);
}(function(Recorder,i18n,$T,isBrowser){
"use strict";

/**
本方法用来生成单个按键信号pcm数据，属于底层方法，要混合多个按键信号到别的pcm中请用封装好的DTMF_EncodeMix方法

参数：
	key: 单个按键0-9#*
	sampleRate:123 要生成的pcm采样率
	duration:100 按键音持续时间
	mute:50 按键音前后静音时长
返回：
	pcm：[Int16,...]，生成单个按键信号
**/
Recorder.DTMF_Encode=function(key,sampleRate,duration,mute){
	var durSize=Math.floor(sampleRate*(duration||100)/1000);
	var muteSize=Math.floor(sampleRate*(mute==null?50:mute)/1000);
	var pcm0=new Int16Array(durSize+muteSize*2);
	var pcm1=new Int16Array(durSize+muteSize*2);
	
	// https://github.com/watilde/node-dtfm/blob/master/encode.js
	var f0=DTMF_Freqs[key][0];
	var f1=DTMF_Freqs[key][1];
	var vol=0.3;
	for(var i=0;i<durSize;i++){
		var v0=vol*Math.sin((2 * Math.PI) * f0 * (i / sampleRate));
		var v1=vol*Math.sin((2 * Math.PI) * f1 * (i / sampleRate));
		pcm0[i+muteSize]=Math.max(-1,Math.min(1,v0))*0x7FFF;
		pcm1[i+muteSize]=Math.max(-1,Math.min(1,v1))*0x7FFF;
	};
	
	//简单叠加 低群 和 高群 信号
	Mix(pcm0,0,pcm1,0);
	return pcm0;
};


/**返回EncodeMix对象，将输入的按键信号混合到持续输入的pcm流中，当.mix(inputPcms)提供的太短的pcm会无法完整放下一个完整的按键信号，所以需要不停调用.mix(inputPcms)进行混合**/
Recorder.DTMF_EncodeMix=function(set){
	return new EncodeMix(set);
};
var EncodeMix=function(set){
	var This=this;
	This.set={
		duration:100 //按键信号持续时间 ms，最小值为30ms
		,mute:25 //按键音前后静音时长 ms，取值为0也是可以的
		,interval:200 //两次按键信号间隔时长 ms，间隔内包含了duration+mute*2，最小值为120ms
	};
	for(var k in set){
		This.set[k]=set[k];
	};
	
	This.keys="";
	This.idx=0;
	This.state={keyIdx:-1,skip:0};
};
EncodeMix.prototype={
	/** 添加一个按键或多个按键 "0" "123#*"，后面慢慢通过mix方法混合到pcm中，无返回值 **/
	add:function(keys){
		this.keys+=keys;
	}
	/** 将已添加的按键信号混合到pcm中，pcms:[[Int16,...],...]二维数组，sampleRate：pcm的采样率，index：pcms第一维开始索引，将从这个pcm开始混合。
	返回混合状态对象。
	注意：调用本方法会修改pcms中的内容，因此混合结果就在pcms内。 **/
	,mix:function(pcms,sampleRate,index){
		index||(index=0);
		var This=this,set=This.set;
		var newEncodes=[];
		
		var state=This.state;
		var pcmPos=0;
		loop:
		for(var i0=index;i0<pcms.length;i0++){
			var pcm=pcms[i0];
			
			var key=This.keys.charAt(This.idx);
			if(!key){//没有需要处理的按键，把间隔消耗掉
				state.skip=Math.max(0, state.skip-pcm.length);
			} else while(key){
				//按键间隔处理
				if(state.skip){
					var op=pcm.length-pcmPos;
					if(op<=state.skip){
						state.skip-=op;
						pcmPos=0;
						continue loop;
					};
					pcmPos+=state.skip;
					state.skip=0;
				};
				
				var keyPcm=state.keyPcm;
				
				//这个key已经混合过，看看有没有剩余的信号
				if(state.keyIdx==This.idx){
					if(state.cur>=keyPcm.length){
						state.keyIdx=-1;
					};
				};
				//新的key，生成信号
				if(state.keyIdx!=This.idx){
					keyPcm=Recorder.DTMF_Encode(key,sampleRate,set.duration,set.mute);
					state.keyIdx=This.idx;
					state.cur=0;
					state.keyPcm=keyPcm;
					
					newEncodes.push({
						key:key
						,data:keyPcm
					});
				};
				
				//将keyPcm混合到当前pcm中，实际是替换逻辑
				var res=Mix(pcm,pcmPos,keyPcm,state.cur,true);
				state.cur=res.cur;
				pcmPos=res.last;
				
				//下一个按键
				if(res.cur>=keyPcm.length){
					This.idx++;
					key=This.keys.charAt(This.idx);
					state.skip=Math.floor(sampleRate*(set.interval-set.duration-set.mute*2)/1000);
				};
				
				//当前pcm的位置已消耗完
				if(res.last>=pcm.length){
					pcmPos=0;
					continue loop;//下一个pcm
				};
			};
		};
		
		return {
			newEncodes:newEncodes //本次混合新生成的按键信号列表 [{key:"*",data:[Int16,...]},...]，如果没有产生新信号将为空数组
			,hasNext:This.idx<This.keys.length //是否还有未混合完的信号
		};
	}
};




//teach.realtime.mix_multiple 抄过来的简单混合算法
var Mix=function(buffer,pos1,add,pos2,mute){
	for(var j=pos1,cur=pos2;;j++,cur++){
		if(j>=buffer.length || cur>=add.length){
			return {
				last:j
				,cur:cur
			};
		};
		
		if(mute){
			buffer[j]=0;//置为0即为静音
		};
		var data_mix,data1=buffer[j],data2=add[cur];
		
		//简单混音算法 https://blog.csdn.net/dancing_night/article/details/53080819
		if(data1<0 && data2<0){
			data_mix = data1+data2 - (data1 * data2 / -0x7FFF);  
		}else{
			data_mix = data1+data2 - (data1 * data2 / 0x7FFF);
		};
		
		buffer[j]=data_mix;
	};
};



var DTMF_Freqs={
	 '1': [697, 1209] ,'2': [697, 1336] ,'3': [697, 1477] ,'A': [697, 1633]
	,'4': [770, 1209] ,'5': [770, 1336] ,'6': [770, 1477] ,'B': [770, 1633]
	,'7': [852, 1209] ,'8': [852, 1336] ,'9': [852, 1477] ,'C': [852, 1633]
	,'*': [941, 1209] ,'0': [941, 1336] ,'#': [941, 1477] ,'D': [941, 1633]
};

	
}));