/*
录音 RecordApp: 微信小程序支持文件，支持在微信小程序环境中使用
https://github.com/xiangyuecn/Recorder

录音功能由微信小程序的RecorderManager录音接口提供（已屏蔽10分钟录音限制），因为js层已加载Recorder和相应的js编码引擎，所以，Recorder支持的录音格式，小程序内均可以做到支持。
*/
(function(factory){
	var browser=typeof window=="object" && !!window.document;
	var win=browser?window:Object; //非浏览器环境，Recorder挂载在Object下面
	var rec=win.Recorder,ni=rec.i18n;
	factory(rec,ni,ni.$T,browser);
}(function(Recorder,i18n,$T,isBrowser){
"use strict";

var IsWx=typeof wx=="object" && !!wx.getRecorderManager;
var App=Recorder.RecordApp;
var CLog=App.CLog;

var platform={
	Support:function(call){
		if(IsWx && isBrowser){ //有的h5里面有wx对象，又有的wx里面有window对象
			var win=window,doc=win.document,loc=win.location,body=doc.body;
			if(loc && loc.href && loc.reload && body && body.appendChild){
				CLog("识别是浏览器但又检测到wx",3);
				call(false); return; //多判断一些稳妥一点
			}
		}
		call(IsWx);
	}
	,CanProcess:function(){
		return true;//支持实时回调
	}
};
App.RegisterPlatform("miniProgram-wx",platform);



//当使用到录音的页面onShow时进行一次调用，用于恢复被暂停的录音（比如按了home键会暂停录音）
App.MiniProgramWx_onShow=function(){
	recOnShow();
};



/*******实现统一接口*******/
platform.RequestPermission=function(sid,success,fail){
	requestPermission(success,fail);
};
platform.Start=function(sid,set,success,fail){
	onRecFn.param=set;
	var rec=Recorder(set);
	rec.set.disableEnvInFix=true; //不要音频输入丢失补偿
	rec.dataType="arraybuffer";
	
	onRecFn.rec=rec;//等待第一个数据到来再调用rec.start
	App.__Rec=rec;//App需要暴露出使用到的rec实例
	
	recStart(success,fail);
};
platform.Stop=function(sid,success,fail){
	clearCurMg();
	
	var failCall=function(msg){
		if(App.__Sync(sid)){
			onRecFn.rec=null;
		}
		fail(msg);
	};
	var rec=onRecFn.rec;
	onRecFn.rec=null;
	
	var clearMsg=success?"":App.__StopOnlyClearMsg();
	if(!rec){
		failCall("未开始录音"+(clearMsg?" ("+clearMsg+")":""));
		return;
	};
	
	CLog("rec encode: pcm:"+rec.recSize+" srcSR:"+rec.srcSampleRate+" set:"+JSON.stringify(onRecFn.param));
	
	var end=function(){
		if(App.__Sync(sid)){
			//把可能变更的配置写回去
			for(var k in rec.set){
				onRecFn.param[k]=rec.set[k];
			};
		};
	};
	if(!success){
		end();
		failCall(clearMsg);
		return;
	};
	rec.stop(function(arrBuf,duration,mime){
		end();
		success(arrBuf,duration,mime);
	},function(msg){
		end();
		failCall(msg);
	});
};




var onRecFn=function(pcm,sampleRate){
	var rec=onRecFn.rec;
	if(!rec){
		CLog("未开始录音，但收到wx PCM数据",3);
		return;
	};
	if(!rec._appStart){
		rec.envStart({
			envName:platform.Key,canProcess:platform.CanProcess()
		},sampleRate);
	};
	rec._appStart=1;
	
	var sum=0;
	for(var i=0;i<pcm.length;i++){
		sum+=Math.abs(pcm[i]);
	}
	
	rec.envIn(pcm,sum);
};



/*******微信小程序录音接口调用*******/
var hasPermission=false;
var requestPermission=function(success,fail){
	clearCurMg();
	initSys();
	if(hasPermission){
		success(); return;
	}
	var mg=wx.getRecorderManager(),next=1;
	mg.onStart(function(){
		hasPermission=true;
		if(next){ next=0;
			stopMg(mg);
			success();
		}
	});
	mg.onError(function(res){
		var msg="请求录音权限出现错误："+res.errMsg;
		CLog(msg+"。"+UserPermissionMsg,1,res);
		if(next){ next=0;
			stopMg(mg);
			fail(msg,true);
		}
	});
	newStart("req",mg);
};
var UserPermissionMsg="请自行检查wx.getSetting中的scope.record录音权限，如果用户拒绝了权限，请引导用户到小程序设置中授予录音权限。";

var curMg,mgStime=0;
var clearCurMg=function(){
	var old=curMg;curMg=null;
	if(old){ stopMg(old) }
};
var stopMg=function(mg){
	mgStime=Date.now();
	mg.stop();
};
var newStart=function(tag,mg){ //统一参数进行start调用，不然开发工具上热更新参数不一样直接卡死
	var obj={
		duration:600000
		,sampleRate:48000 //pc端无效
		,encodeBitRate:320000
		,numberOfChannels:1
		,format:"PCM"
		,frameSize:isDev?1:4 //4=48/12
	};
	var set=onRecFn.param||{},aec=(set.audioTrackSet||{}).echoCancellation;
	if(sys.platform=="android"){ //Android指定麦克风源 MediaRecorder.AudioSource，0 DEFAULT 默认音频源，1 MIC 主麦克风，5 CAMCORDER 相机方向的麦，6 VOICE_RECOGNITION 语音识别，7 VOICE_COMMUNICATION 语音通信(带回声消除)
		var source=set.android_audioSource,asVal="";
		if(source==null && aec) source=7;
		if(source==null) source=App.Default_Android_AudioSource;
		if(source==1) asVal="mic";
		if(source==5) asVal="camcorder";
		if(source==6) asVal="voice_recognition";
		if(source==7) asVal="voice_communication";
		if(asVal)obj.audioSource=asVal;
	};
	if(aec){
		CLog("mg注意：iOS下无法配置回声消除，Android无此问题，建议都启用听筒播放避免回声：wx.setInnerAudioOption({speakerOn:false})",3);
	};
	CLog("["+tag+"]mg.start obj",obj);
	mg.start(obj);
};
var recOnShow=function(){
	if(curMg && curMg.__pause){
		CLog("mg onShow 录音开始恢复...",3);
		curMg.resume();
	}
};
var recStart=function(success,fail){
	clearCurMg();
	initSys();
	devWebMInfo={};
	if(isDev){
		CLog("RecorderManager.onFrameRecorded 在开发工具中测试返回的是webm格式音频，将会尝试进行解码。开发工具中录音偶尔会非常卡，建议使用真机测试（各种奇奇怪怪的毛病就都正常了）",3);
	}
	
	var startIsEnd=false,startCount=1;
	var startEnd=function(err){
		if(startIsEnd)return; startIsEnd=true;
		if(err){
			clearCurMg();
			fail(err);
		}else{
			success();
		};
	};
	
	var mg=curMg=wx.getRecorderManager();
	mg.onInterruptionEnd(function(){
		if(mg!=curMg)return;
		CLog("mg onInterruptionEnd 录音开始恢复...",3);
		mg.resume();
	});
	mg.onPause(function(){
		if(mg!=curMg)return;
		mg.__pause=Date.now();
		CLog("mg onPause 录音被打断",3);
	});
	mg.onResume(function(){
		if(mg!=curMg)return;
		var t=mg.__pause?Date.now()-mg.__pause:0,t2=0;
		mg.__pause=0;
		if(t>300){//填充最多1秒的静默
			t2=Math.min(1000,t);
			onRecFn(new Int16Array(48000/1000*t2),48000);
		}
		CLog("mg onResume 恢复录音，填充了"+t2+"ms静默",3);
	});
	mg.onError(function(res){
		if(mg!=curMg)return;
		var msg=res.errMsg,tag="mg onError 开始录音出错：";
		if(!startIsEnd && !mg._srt && /fail.+is.+recording/i.test(msg)){
			var st=600-(Date.now()-mgStime); //距离上次停止未超过600毫秒，重试
			if(st>0){ st=Math.max(100,st);
				CLog(tag+"等待"+st+"ms重试",3,res);
				setTimeout(function(){
					if(mg!=curMg)return; mg._srt=1;
					CLog(tag+"正在重试",3);
					newStart("retry start",mg);
				}, st);
				return;
			};
		};
		CLog(startCount>1?tag+"可能无法继续录音["+startCount+"]。"+msg
			:tag+msg+"。"+UserPermissionMsg,1,res);
		startEnd("开始录音出错："+msg);
	});
	mg.onStart(function(){
		if(mg!=curMg)return;
		CLog("mg onStart 已开始录音");
		mg._srt=0; //下次开始失败可以重试
		mg._st=Date.now();
		startEnd();
	});
	mg.onStop(function(res){
		CLog("mg onStop 请勿尝试使用此原始结果中的文件路径（此原始文件的格式、采样率等和录音配置不相同）；如需本地文件：可在RecordApp.Stop回调中将得到的ArrayBuffer（二进制音频数据）用RecordApp.MiniProgramWx_WriteLocalFile接口保存到本地，即可得到有效路径。res:",res);
		if(mg!=curMg)return;
		if(!mg._st || Date.now()-mg._st<600){ CLog("mg onStop但已忽略",3); return }
		CLog("mg onStop 已停止录音，正在重新开始录音...");
		startCount++;
		mg._st=0;
		newStart("restart",mg);
	});
	
	var start0=function(){
		mg.onFrameRecorded(function(res){
			if(mg!=curMg)return;
			if(!startIsEnd)CLog("mg onStart未触发，但收到了onFrameRecorded",3);
			startEnd();
			
			var aBuf=res.frameBuffer;
			if(!aBuf || !aBuf.byteLength){
				return;
			}
			if(isDev){
				devWebmDecode(new Uint8Array(aBuf));
			}else{
				onRecFn(new Int16Array(aBuf),48000);
			};
		});
		newStart("start",mg);
	};
	
	var st=600-(Date.now()-mgStime); //距离上次停止未超过600毫秒，等待一会，一般是第一次请求权限后立马开始录音造成的（录音参数不一样，不共享同一个mg）
	if(st>0){ st=Math.max(100,st);
		CLog("mg.start距stop太近需等待"+st+"ms",3);
		setTimeout(function(){ if(mg!=curMg)return; start0(); }, st);
	}else{
		start0();
	};
};








//保存文件到本地，提供文件名或set和arrayBuffer，True(savePath)，False(errMsg)
App.MiniProgramWx_WriteLocalFile=function(fileName,buffer,True,False){
	var set=fileName; if(typeof(set)=="string") set={fileName:fileName};
	fileName=set.fileName;
	var append=set.append; //追加写入到文件结尾
	var seek_=set.seekOffset, seek=+seek_||0; //覆盖写入到指定位置
	if(!seek_ && seek_!==0) seek=-1;
	
	var EnvUsr=wx.env.USER_DATA_PATH, savePath=fileName;
	if(fileName.indexOf(EnvUsr)==-1) savePath=EnvUsr+"/"+fileName;
	
	//如果上次还在写入，就等待，保证顺序写入
	var tasks=writeTasks[savePath]=writeTasks[savePath]||[];
	var tk0=tasks[0], tk={a:set,b:buffer,c:True,d:False};
	if(tk0 && tk0._r){ //还在写入，等待
		CLog("wx文件等待写入"+savePath,3);
		set._tk=1; tasks.push(tk); return;
	}
	if(set._tk) CLog("wx文件继续写入"+savePath);
	tasks.splice(0,0,tk); tk._r=1; //阻塞后续写入
	
	var mg=wx.getFileSystemManager(), fd=0;
	var endCall=function(){ //操作完成 清理环境，延迟一下等操作完全结束
		if(fd) mg.close({ fd:fd });
		setTimeout(function(){
			tasks.shift(); var tk=tasks.shift();
			if(tk){ //继续写入等待的
				App.MiniProgramWx_WriteLocalFile(tk.a,tk.b,tk.c,tk.d);
			}
		});
	};
	var okCall=function(){ endCall(); True&&True(savePath) };
	var failCall=function(e){ endCall();
		var msg=e.errMsg||"-";
		CLog("wx文件"+savePath+"写入出错："+msg,1);
		False&&False(msg);
	};
	
	if(seek>-1 || append){
		mg.open({
			filePath:savePath ,flag:seek>-1?"r+":"a"
			,success:function(res){
				fd=res.fd;
				var opt={ fd:fd, data:buffer, success:okCall, fail:failCall };
				if(seek>-1) opt.position=seek;
				mg.write(opt);
			}
			,fail:failCall
		});
	}else{
		mg.writeFile({
			filePath:savePath, encoding:"binary", data:buffer
			,success:okCall, fail:failCall
		});
	}
};
var writeTasks={};
//删除已保存到本地的文件，savePath必须是WriteLocalFile得到的路径 True() False(errMsg)
App.MiniProgramWx_DeleteLocalFile=function(savePath,True,False){
	wx.getFileSystemManager().unlink({
		filePath:savePath
		,success:function(){ True&&True() }
		,fail:function(e){ False&&False(e.errMsg||"-") }
	});
};





var isDev,sys;
var initSys=function(){
	if(sys)return;
	sys=wx.getSystemInfoSync();
	isDev=sys.platform=="devtools"?1:0;
	if(isDev){
		devWebCtx=wx.createWebAudioContext();
	}
};


/****开发工具内录音返回的webm数据解码成pcm，方便测试****/
var devWebCtx,devWebMInfo;
//=======从WebM字节流中提取pcm数据=====
var devWebmDecode=function(inBytes){
	var scope=devWebMInfo;
	if(!scope.pos){
		scope.pos=[0]; scope.tracks={}; scope.bytes=[];
	};
	var tracks=scope.tracks, position=[scope.pos[0]];
	var endPos=function(){ scope.pos[0]=position[0] };
	
	var sBL=scope.bytes.length;
	var bytes=new Uint8Array(sBL+inBytes.length);
	bytes.set(scope.bytes); bytes.set(inBytes,sBL);
	scope.bytes=bytes;
	
	//检测到不是webm，当做pcm直接返回
	var returnPCM=function(){
		scope.bytes=[];
		onRecFn(new Int16Array(bytes),48000);
	};
	if(scope.isNotWebM){
		returnPCM(); return;
	};
	
	//先读取文件头和Track信息
	if(!scope._ht){
		//暴力搜索EBML Header，开头数据可能存在上次录音结尾数据
		var headPos0=0;
		for(var i=0;i<bytes.length;i++){
			if(bytes[i]==0x1A && bytes[i+1]==0x45 && bytes[i+2]==0xDF && bytes[i+3]==0xA3){
				headPos0=i;
				position[0]=i+4; break;
			}
		}
		if(!position[0]){
			if(bytes.length>5*1024){
				CLog("未识别到WebM数据，开发工具可能已支持PCM",3);
				scope.isNotWebM=true;
				returnPCM();
			};
			return;//未识别到EBML Header
		}
		readMatroskaBlock(bytes, position);//跳过EBML Header内容
		if(!BytesEq(readMatroskaVInt(bytes, position), [0x18,0x53,0x80,0x67])){
			return;//未识别到Segment
		}
		readMatroskaVInt(bytes, position);//跳过Segment长度值
		while(position[0]<bytes.length){
			var eid0=readMatroskaVInt(bytes, position);
			var bytes0=readMatroskaBlock(bytes, position);
			var pos0=[0],audioIdx=0;
			if(!bytes0)return;//数据不全，等待缓冲
			//Track完整数据，循环读取TrackEntry
			if(BytesEq(eid0, [0x16,0x54,0xAE,0x6B])){
				scope._ht=bytes.slice(headPos0,position[0]);
				CLog("WebM Tracks",tracks);
				endPos();
				break;
			}
		}
	}
	
	//循环读取Cluster内的SimpleBlock
	var datas=[],dataLen=0;
	while(position[0]<bytes.length){
		var p0=position[0];
		var eid1=readMatroskaVInt(bytes, position);
		var p1=position[0];
		var bytes1=readMatroskaBlock(bytes, position);
		if(!bytes1)break;//数据不全，等待缓冲
		if(BytesEq(eid1, [0xA3])){//SimpleBlock完整数据
			var arr=bytes.slice(p0,position[0]);
			dataLen+=arr.length;
			datas.push(arr);
		}
		endPos();
	}
	
	if(!dataLen){
		return;
	}
	var more=new Uint8Array(bytes.length-scope.pos[0]);
	more.set(bytes.subarray(scope.pos[0]));
	scope.bytes=more; //清理已读取了的缓冲数据
	scope.pos[0]=0;
	
	//和头一起拼接成新的webm
	var add=[0x1F,0x43,0xB6,0x75,0x01,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF];//Cluster
	add.push(0xE7,0x81,0x00);
	dataLen+=add.length;
	datas.splice(0,0,add);
	
	dataLen+=scope._ht.length;
	datas.splice(0,0,scope._ht);
	
	var u8arr=new Uint8Array(dataLen); //已获取的音频数据
	for(var i=0,i2=0;i<datas.length;i++){
		u8arr.set(datas[i],i2);
		i2+=datas[i].length;
	}
	
	devWebCtx.decodeAudioData(u8arr.buffer, function(raw){
		var src=raw.getChannelData(0);
		var pcm=new Int16Array(src.length);
		for(var i=0;i<src.length;i++){
			var s=Math.max(-1,Math.min(1,src[i]));
			s=s<0?s*0x8000:s*0x7FFF;
			pcm[i]=s;
		};
		onRecFn(pcm,raw.sampleRate);
	},function(){
		CLog("WebM解码失败",1);
	});
};
//两个字节数组内容是否相同
var BytesEq=function(bytes1,bytes2){
	if(!bytes1 || bytes1.length!=bytes2.length) return false;
	if(bytes1.length==1) return bytes1[0]==bytes2[0];
	for(var i=0;i<bytes1.length;i++){
		if(bytes1[i]!=bytes2[i]) return false;
	}
	return true;
};
//字节数组BE转成int数字
var BytesInt=function(bytes){
	var s="";//0-8字节，js位运算只支持4字节
	for(var i=0;i<bytes.length;i++){var n=bytes[i];s+=(n<16?"0":"")+n.toString(16)};
	return parseInt(s,16)||0;
};
//读取一个可变长数值字节数组
var readMatroskaVInt=function(arr,pos,trim){
	var i=pos[0];
	if(i>=arr.length)return;
	var b0=arr[i],b2=("0000000"+b0.toString(2)).substr(-8);
	var m=/^(0*1)(\d*)$/.exec(b2);
	if(!m)return;
	var len=m[1].length, val=[];
	if(i+len>arr.length)return;
	for(var i2=0;i2<len;i2++){ val[i2]=arr[i]; i++; }
	if(trim) val[0]=parseInt(m[2]||'0',2);
	pos[0]=i;
	return val;
};
//读取一个自带长度的内容字节数组
var readMatroskaBlock=function(arr,pos){
	var lenVal=readMatroskaVInt(arr,pos,1);
	if(!lenVal)return;
	var len=BytesInt(lenVal);
	var i=pos[0], val=[];
	if(len<0x7FFFFFFF){ //超大值代表没有长度
		if(i+len>arr.length)return;
		for(var i2=0;i2<len;i2++){ val[i2]=arr[i]; i++; }
	}
	pos[0]=i;
	return val;
};
//=====End WebM读取=====


}));