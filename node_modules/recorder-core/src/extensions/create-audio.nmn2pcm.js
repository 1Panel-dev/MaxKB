/***
简单用 正弦波、方波、锯齿波、三角波 函数生成一段音乐简谱的pcm数据，主要用于测试时提供音频数据。本可音频生成插件可以移植到其他语言环境，如需定制可联系作者
https://github.com/xiangyuecn/Recorder

此插件在线生成测试：assets/runtime-codes/test.create-audio.nmn2pcm.js

var pcmData=Recorder.NMN2PCM(set);
	set配置：{
		texts:""|["",""] 简谱格式化文本，如果格式不符合要求，将会抛异常
		sampleRate: 生成pcm的采样率，默认48000；取值不能过低，否则会削除高音
		timbre: 音色，默认2.0（使用音符对应频率的一个倍频），取值>=1.0
		meterDuration: 一拍时长，毫秒，默认600ms
		muteDuration: 音符之间的静默，毫秒，0时无静默，默认meterDur/4（最大50ms）
		beginDuration: 开头的静默时长，毫秒，0时无静默，默认为200ms
		endDuration: 结尾的静默时长，毫秒，0时无静默，默认为200ms
		
		volume: 音量，默认0.3，取值范围0.0-1.0（最大值1）
		waveType: 波形发生器类型，默认"sine"，取值：sine(正弦波)、square(方波，volume应当减半)、sawtooth(锯齿波)、triangle(三角波)
	}

	texts格式：单个文本，或文本数组
		- 四分音符(一拍)：低音: 1.-7. 中音: 1-7 高音: 1'-7' 休止符(静音)：0
		- 音符后面用 "." 表示低音（尽量改用"."：".." 倍低音，"..." 超低音）
		- 音符后面用 "'" 表示高音（尽量改用"'"："''" 倍高音，"'''" 超高音）
		- 音符之间用 "|" 或 " " 分隔一拍
		- 一拍里面多个音符用 "," 分隔，每个音按权重分配这一拍的时长占比，如：“6,7”为一拍，6、7各占1/2拍，相当于八分音符
		
		- 音符后面用 "-" 表示二分音符，简单计算为1+1=2拍时长，几个-就加几拍
		- 音符后面用 "_" 表示八分音符；两两在一拍里面的音符可以免写_，自动会按1/2分配；一拍里面只有一个音时这拍会被简单计算为1/2=0.5拍；其他情况计算会按权重分配这一拍的时长(复杂)，如：“6,7_”为1/2+1/2/2=0.75拍（“6*,7_”才是(1+0.5)/2+1/2/2=1拍），其中6权重1分配1/2=0.5拍，7权重0.5分配1/2/2=0.25拍；多加一个"_"就多除个2：“6_,7_”是1/2+1/2=1拍（等同于“6,7”可免写_）；“6__,7__”是1/2/2+1/2/2=0.5拍；只要权重加起来是整数就算作完整的1拍
		- 音符后面用 "*" 表示1+0.5=1.5拍，多出来的1/2计算和_相同(复杂)，"**"两个表示加0.25
		
		- 可以使用 "S"(sine) "Q"(square) "A"(sawtooth) "T"(triangle) 来切换后续波形发生器类型（按一拍来书写，但不占用时长），类型后面可以接 "(2.0)" 来设置音色，接 "[0.5]" 来设置音量（为set.volume*0.5）；特殊值 "R"(reset) 可重置类型成set配置值，如果R后面没有接音色或音量也会被重置；比如："1 2|A(4.0)[0.6] 3 4 R|5 6"，其中12 56使用set配置的类型和音色音量，34使用锯齿波、音色4.0、音量0.18=0.3*0.6
		
		- 如果同时有多个音，必须提供数组格式，每个音单独提供一个完整简谱（必须同步对齐）

	返回结果：{
		pcm: Int16Array，pcm数据
		duration: 123 pcm的时长，单位毫秒
		set: {...} 使用的set配置
		warns: [] 不适合抛异常的提示消息
	}

Recorder.NMN2PCM.GetExamples() 可获取内置的简谱
***/
(function(factory){
	var browser=typeof window=="object" && !!window.document;
	var win=browser?window:Object; //非浏览器环境，Recorder挂载在Object下面
	var rec=win.Recorder,ni=rec.i18n;
	factory(rec,ni,ni.$T,browser);
}(function(Recorder,i18n,$T,isBrowser){
"use strict";

var NMN2PCM=function(set){
	var texts=set.texts||[]; if(typeof(texts)=="string") texts=[texts];
	var setSR=set.sampleRate, sampleRate=setSR; if(!sampleRate || sampleRate<1)sampleRate=48000;
	var meterDur=set.meterDuration||600;
	var timbre=set.timbre||2; if(timbre<1)timbre=1;
	
	var volume=set.volume; if(volume==null)volume=0.3;
	volume=Math.max(0,volume); volume=Math.min(1,volume);
	
	var waveType=set.waveType||"";
	if(",sine,square,sawtooth,triangle,".indexOf(","+waveType+",")==-1)waveType="";
	waveType=waveType||"sine";
	
	var muteDur=set.muteDuration;
	if(muteDur==null || muteDur<0){
		muteDur=meterDur/4; if(muteDur>50)muteDur=50;
	}
	var mute0=new Int16Array(sampleRate*muteDur/1000);
	
	var beginDur=set.beginDuration;
	if(beginDur==null || beginDur<0) beginDur=200;
	var beginMute=new Int16Array(sampleRate*beginDur/1000);
	var endDur=set.endDuration;
	if(endDur==null || endDur<0) endDur=200;
	var endMute=new Int16Array(sampleRate*endDur/1000);
	
	//生成C调频率 A=440 国际标准音
	var s=function(s){ return 440/Math.pow(2,s/12) };
	var Freqs=[s(9),s(7),s(5),s(4),s(2),s(0),s(-2)];
	var FreqMP={};
	for(var i=1;i<=7;i++){
		var v=Freqs[i-1];
		FreqMP[i+"..."]=v/8;
		FreqMP[i+".."]=v/4;
		FreqMP[i+"."]=v/2;
		FreqMP[i]=v;
		FreqMP[i+"'"]=v*2;
		FreqMP[i+"''"]=v*4;
		FreqMP[i+"'''"]=v*8;
	}
	
	var tracks=[],freqMax=0,freqMin=90000;
	for(var iT=0;setSR!=-1 && iT<texts.length;iT++){
		var meters=texts[iT].split(/[\s\|]+/);
		var buffers=[],size=0,wType=waveType,wTimbre=timbre,wVol=volume;
		for(var i0=0;i0<meters.length;i0++){
			var txt0=meters[i0]; if(!txt0)continue;
			var v0=txt0.charCodeAt(0);
			if(v0<48 || v0>55){//不是0-7，切换波形或音色
				var m=/^(\w)(?:\((.+)\)|\[(.+)\])*$/.exec(txt0)||[],mT=m[1];
				var m=/\((.+)\)/.exec(txt0)||[],mTb=m[1];
				var m=/\[(.+)\]/.exec(txt0)||[],mVol=m[1];
				if(mT=="R"){ wType=waveType;wTimbre=timbre;wVol=volume; }
				else if(mT=="S") wType="sine";
				else if(mT=="Q") wType="square";
				else if(mT=="A") wType="sawtooth";
				else if(mT=="T") wType="triangle";
				else mT="";
				if(!mT||mTb&&!+mTb||mVol&&!+mVol)throw new Error("Invalid: "+txt0);
				if(mTb)wTimbre=+mTb;
				if(mVol)wVol=volume*mVol;
				continue;
			}
			var ys=txt0.split(",");//一拍里面的音符
			var durTotal=meterDur; //一拍的时长，如果里面有+，代表多拍
			var bTotal=0,hasG=0,hasX=0;
			for(var i2=0;i2<ys.length;i2++){//先计算出每个音符的占用时长比例
				var vs=ys[i2].split("");
				var o={ y:vs[0],b:1,t:wType,tb:wTimbre,vol:wVol }; ys[i2]=o;
				for(var i3=1;i3<vs.length;i3++){
					var v=vs[i3];
					if(v=="'") o.y+="'";
					else if(v==".") o.y+=".";
					else if(v=="-"){ o.b+=1; durTotal+=meterDur; }
					else if(v=="_"){ o.b/=2; hasG=1; }
					else if(v=="*" && !hasX){ o.b+=0.5; hasX=0.5;
							if(vs[i3+1]=="*"){ o.b-=0.25; hasX=0.25; i3++; } }
					else throw new Error($T("3RBa::符号[{1}]无效：{2}",0,v,txt0));
				}
				bTotal+=o.b;
			}
			if(bTotal%1>0){
				if(hasG){//"_"不够数量，减掉时间
					durTotal*=bTotal/Math.ceil(bTotal);
				}else if(hasX){//"*"加上1/2|1/4拍的时间
					durTotal+=meterDur*hasX;
				}
			}
			durTotal-=ys.length*muteDur;//减掉中间的静默
			for(var i2=0;i2<ys.length;i2++){//生成每个音符的pcm
				var o=ys[i2],wType=o.t,wTimbre=o.tb,wVol=o.vol,freq=FreqMP[o.y]||0;
				if(!freq && o.y!="0") throw new Error($T("U212::音符[{1}]无效：{2}",0,o.y,txt0));
				freq=freq*wTimbre;
				var dur=durTotal*o.b/bTotal;
				var pcm=new Int16Array(Math.round(dur/1000*sampleRate));
				if(freq){
					freqMax=Math.max(freqMax,freq);
					freqMin=Math.min(freqMin,freq);
					//不同波形算法取自 https://github.com/cristovao-trevisan/wave-generator/blob/master/index.js
					if(wType=="sine"){//正弦波
						var V=(2 * Math.PI) * freq / sampleRate;
						for(var i=0;i<pcm.length;i++){
							var v=wVol*Math.sin(V * i);
							pcm[i]=Math.max(-1,Math.min(1,v))*0x7FFF;
						}
					}else if(wType=="square"){//方波
						var V=sampleRate / freq;
						for(var i=0;i<pcm.length;i++){
							var v=wVol*((i % V) < (V / 2) ? 1 : -1);
							pcm[i]=Math.max(-1,Math.min(1,v))*0x7FFF;
						}
					}else if(wType=="sawtooth"){//锯齿波
						var V=sampleRate / freq;
						for(var i=0;i<pcm.length;i++){
							var v=wVol*(-1 + 2 * (i % V) / V);
							pcm[i]=Math.max(-1,Math.min(1,v))*0x7FFF;
						}
					}else if(wType=="triangle"){//三角波
						var V=sampleRate / freq;
						for(var i=0;i<pcm.length;i++){
							var Vi = (i + V / 4) % V;
							var v=wVol*(Vi<V/2?(-1+4*Vi/V):(3-4*Vi/V));
							pcm[i]=Math.max(-1,Math.min(1,v))*0x7FFF;
						}
					}
					var pcmDur4=~~(pcm.length/sampleRate*1000/4)||1;
					FadeInOut(pcm,sampleRate,Math.min(pcmDur4, 10));
				}
				
				var mute=mute0; if(!buffers.length)mute=beginMute;
				buffers.push(mute); size+=mute.length;
				
				buffers.push(pcm); size+=pcm.length;
			}
		}
		if(size>0){
			buffers.push(endMute); size+=endMute.length;
			tracks.push({buffers:buffers,size:size});
		}
	}
	tracks.sort(function(a,b){return b.size-a.size});
	
	var pcm=new Int16Array(tracks[0]&&tracks[0].size||0);
	for(var iT=0;iT<tracks.length;iT++){
		var o=tracks[iT],buffers=o.buffers,size=o.size;
		if(iT==0){
			for(var i=0,offset=0;i<buffers.length;i++){
				var buf=buffers[i];
				pcm.set(buf,offset);
				offset+=buf.length;
			}
		}else{
			var diffMs=(pcm.length-size)/sampleRate*1000;
			if(diffMs>10){//10毫秒误差
				throw new Error($T("7qAD::多个音时必须对齐，相差{1}ms",0,diffMs));
			};
			for(var i=0,offset=0;i<buffers.length;i++){
				var buf=buffers[i];
				for(var j=0;j<buf.length;j++){
					var data_mix,data1=pcm[offset],data2=buf[j];
					
					//简单混音算法 https://blog.csdn.net/dancing_night/article/details/53080819
					if(data1<0 && data2<0){
						data_mix = data1+data2 - (data1 * data2 / -0x7FFF);  
					}else{
						data_mix = data1+data2 - (data1 * data2 / 0x7FFF);
					};
					
					pcm[offset++]=data_mix;
				}
			}
		}
	}
	
	var dur=Math.round(pcm.length/sampleRate*1000);
	var Warns=[],minSR=~~(freqMax*2);
	if(freqMax && sampleRate<minSR){
		var msg="sampleRate["+sampleRate+"] should be greater than "+minSR;
		Warns.push(msg); Recorder.CLog("NMN2PCM: "+msg,3);
	}
	
	return {pcm:pcm, duration:dur, warns:Warns, set:{
		texts:texts, sampleRate:sampleRate, timbre:timbre, meterDuration:meterDur
		,muteDuration:muteDur, beginDuration:beginDur, endDuration:endDur
		,volume:volume,waveType:waveType
	}};
};


/**pcm数据进行首尾1ms淡入淡出处理，播放时可以大幅减弱爆音**/
var FadeInOut=NMN2PCM.FadeInOut=function(arr,sampleRate,dur){
	var sd=sampleRate/1000*(dur||1);//浮点数，arr是Int16或者Float32
	for(var i=0;i<sd;i++){
		arr[i]*=i/sd;
	}
	for(var l=arr.length,i=~~(l-sd);i<l;i++){
		arr[i]*=(l-i)/sd;
	}
};






/***内置部分简谱*****/
NMN2PCM.GetExamples=function(){ return {

DFH:{//前3句，https://www.hnchemeng.com/liux/201807/68393.html
	name:"东方红"
	,get:function(sampleRate){
		return NMN2PCM({ //https://www.bilibili.com/video/BV1VW4y1v7nY?p=2
			sampleRate:sampleRate
			,meterDuration:1000
			,timbre:3
			,texts:"5 5,6|2-|1 1,6.|2-|5 5|6,1' 6,5|1 1,6.|2-"
		});
	}
}
,HappyBirthday:{//4句，https://www.zaoxu.com/jjsh/bkdq/310228.html
	name:$T("QGsW::祝你生日快乐")
	,get:function(sampleRate){
		return NMN2PCM({
			sampleRate:sampleRate
			,meterDuration:450
			,timbre:4
			,waveType:"triangle", volume:0.15
			,texts:"5.,5. 6. 5.|1 7.-|5.,5. 6. 5.|2 1-|5.,5. 5 3|1 7. 6.|4*,4_ 3 1|2 1-"
		});
	}
}
,LHC:{//节选一段，https://www.qinyipu.com/jianpu/jianpudaquan/41703.html
	name:"兰花草（洒水版）"
	,get:function(sampleRate){
		return NMN2PCM({
			sampleRate:sampleRate
			,meterDuration:650
			,timbre:4
			,texts:"6.,3 3,3|3* 2_|1*,2_ 1,7.|6.-|6,6 6,6|6* 5_|3_,5_,5 5,4|3-|3,3_,6_ 6,5|3* 2_|1*,2_ 1,7.|6. 3.|3.,1 1,7.|6.* 2__,3__|2*,1_ 7._,7._,5.|6.-"
		});
	}
}
,ForElise:{//节选一段，https://www.qinyipu.com/jianpu/chunyinle/3023.html
	name:$T("emJR::致爱丽丝")
	,get:function(sampleRate){
		return NMN2PCM({
			sampleRate:sampleRate
			,meterDuration:550
			,muteDuration:20
			,timbre:6
			,texts:"3',2'|3',2' 3',7 2',1'|"
				+"6 0,1 3,6|7 0,3 5,7|1' 0 3',2'|"
				+"3',2' 3',7 2',1'|6 0,1 3,6|7 0,3 1',7|"
				+"6 0,7 1',2'|3' 0,5 4',3'|2' 0,4 3',2'|1' 0,3 2',1'|"
				+"7"
		});
	}
}
,Canon_Right:{//节选一段，https://www.cangqiang.com.cn/d/32153.html
	name:$T("GsYy::卡农-右手简谱")
	,get:function(sampleRate){
		return NMN2PCM({
			sampleRate:sampleRate
			,meterDuration:700
			,texts:"1',7 1',3 5 6,7|"
				+"1' 3' 5',3' 5',6'|4',3' 2',4' 3',2' 1',7|      7 1',2'|"
				+"5',3'_,4'_ 5',3'_,4'_ 5',5,6,7 1',2',3',4'|3',1'_,2'_ 3',3_,4_ 5,6,5,4 5,1',7,1'|"
				+"6,1'_,7_ 6,5_,4_ 5,4,3,4 5,6,7,1'|6,1'_,7_ 1',7_,6_ 7,6,7,1' 2'_,1'_,7|1'-"
		});
	}
}
,Canon:{//开头一段，https://www.kanpula.com/jianpu/21316.html
	name:$T("bSFZ::卡农")
	,get:function(sampleRate){
		var txt1="",txt2="",txt3="",txt4="";
		//(1)
		txt1+="3'---|2'---|1'---|7---|";
		txt2+="1'---|7---|6---|5---|";
		txt3+="5---|5---|3---|3---|";
		txt4+="R[0.3] 1. 5. 1 3|5.. 2. 5. 7.|6.. 3. 6. 1|3.. 7.. 3. 5.|";
		//(5)
		txt1+="6---|5---|6---|7---|";
		txt2+="4---|3---|4---|5---|";
		txt3+="1---|1---|1---|2---|";
		txt4+="4.. 1. 4. 6.|1. 5. 1 3|4.. 1. 4. 6.|5.. 2. 5. 7.|";
		//(9)
		txt1+="3'---|2'---|1'---|7---|";
		txt2+="1'---|7---|6---|5---|";
		txt3+="5---|5---|3---|3-- 5'|";
		txt4+="1. 5. 1 3|5.. 2. 5. 7.|6.. 3. 6. 1|3.. 7.. 3. 5.|";
		//(13)
		txt1+="4' 3' 2' 4'|3' 2' 1' 5|6- 6 1'|7 1' 2'-|";
		txt2+="4.. 1. 4. 6.|1. 5. 1 3|4.. 1. 4. 6.|5.. 2. 5. 7.|";
		txt3+="0---|0---|0---|0---|";
		txt4+="0---|0---|0---|0---|";
		//(17)
		txt1+="3',5 1'_ 5' 5_ 3'|3' 4' 3' 2'|1',3 6_ 3' 3_ 1'|1' 2' 1' 7|";
		txt2+="1. 5. 1 3|5.. 2. 5. 7.|6.. 3. 6. 1|3.. 7.. 3. 5.|";
		txt3+="0---|0---|0---|0---|";
		txt4+="0---|0---|0---|0---|";
		//(21)
		txt1+="6,1 4_ 1' 1_ 6|5,1 3_ 1' 1_ 5|6,1 4_ 1' 1_ 6|7 7 1' 2'|";
		txt2+="4.. 1. 4. 6.|1. 5. 1 3|4.. 1. 4. 6.|5..,5. 5..,5. 6..,6. 6..,6.|";
		txt3+="0---|0---|0---|0---|";
		txt4+="0---|0---|0---|0---|";
		
		return NMN2PCM({
			sampleRate:sampleRate
			,meterDuration:500
			,texts:[txt1,txt2,txt3,txt4]
		});
	}
}
}
};


Recorder.NMN2PCM=NMN2PCM;

}));