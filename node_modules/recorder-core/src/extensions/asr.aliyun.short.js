/*
录音 Recorder扩展，ASR，阿里云语音识别（语音转文字），支持实时语音识别、单个音频文件转文字

https://github.com/xiangyuecn/Recorder

- 本扩展通过调用 阿里云-智能语音交互-一句话识别 接口来进行语音识别，无时长限制。
- 识别过程中采用WebSocket直连阿里云，语音数据无需经过自己服务器。
- 自己服务器仅需提供一个Token生成接口即可（本库已实现一个本地测试NodeJs后端程序 /assets/demo-asr/NodeJsServer_asr.aliyun.short.js）。

本扩展单次语音识别时虽长无限制，最佳使用场景还是1-5分钟内的语音识别；60分钟以上的语音识别本扩展也能胜任（需自行进行重试容错处理），但太长的识别场景不太适合使用阿里云一句话识别（阿里云单次一句话识别最长60秒，本扩展自带拼接过程，所以无时长限制）；为什么采用一句话识别：因为便宜。


【对接流程】
	1. 到阿里云开通 一句话识别 服务（可试用一段时间，正式使用时应当开通商用版，很便宜），得到AccessKey、Secret，参考：https://help.aliyun.com/document_detail/324194.html ；
	2. 到阿里云智能语音交互控制台创建相应的语音识别项目，并配置好项目，得到Appkey，每个项目可以设置一种语言模型，要支持多种语言就创建多个项目；
	3. 需要后端提供一个Token生成接口（用到上面的Key和Secret），可直接参考或本地运行此NodeJs后端测试程序：/assets/demo-asr/NodeJsServer_asr.aliyun.short.js，配置好代码里的阿里云账号后，在目录内直接命令行执行`node NodeJsServer_asr.aliyun.short.js`即可运行提供本地测试接口；
	4. 前端调用ASR_Aliyun_Short，传入tokenApi，即可很简单的实现语音识别功能；

在线测试例子：
	https://xiangyuecn.gitee.io/recorder/assets/工具-代码运行和静态分发Runtime.html?jsname=teach.realtime.asr.aliyun.short
调用示例：
	var rec=Recorder(recSet);rec.open(...) //进行语音识别前，先打开录音，获得录音权限
	
	var asr=Recorder.ASR_Aliyun_Short(set); //创建asr对象，参数详情请参考下面的源码
	
	//asr创建好后，随时调用strat，开始进行语音识别
	asr.start(function(){
		rec.start();//一般在start成功之后，调用rec.start()开始录音，此时可以通知用户讲话了
	},fail);
	
	//实时处理输入音频数据，一般是在rec.set.onProcess中调用本方法，输入实时录制的音频数据，输入的数据将会发送语音识别；不管有没有start，都可以调用本方法，start前输入的数据会缓冲起来等到start后进行识别
	asr.input([[Int16,...],...],48000,0); 
	
	//话讲完后，调用stop结束语音识别，得到识别到的内容文本
	asr.stop(function(text,abortMsg){
		//text为识别到的最终完整内容；如果存在abortMsg代表识别中途被某种错误停止了，text是停止前的内容识别到的完整内容，一般早在asrProcess中会收到abort事件然后要停止录音
	},fail);

更多的方法：
	asr.inputDuration() 获取input已输入的音频数据总时长，单位ms
	asr.sendDuration() 获取已发送识别的音频数据总时长，存在重发重叠部分，因此比inputDuration长
	asr.asrDuration() 获取已识别的音频数据总时长，去除了sendDuration的重叠部分，值<=inputDuration
	asr.getText() 获取实时结果文本，如果已stop返回的就是最终文本，一般无需调用此方法，因为回调中都提供了此方法的返回值
	
	//一次性将单个完整音频Blob文件转成文字，无需start、stop，创建好asr后直接调用本方法即可
	asr.audioToText(audioBlob,success,fail)
	//一次性的将单个完整PCM音频数据转成文字，无需start、stop，创建好asr后直接调用本方法即可
	asr.pcmToText(buffer,sampleRate,success,fail)
*/
(function(factory){
	var browser=typeof window=="object" && !!window.document;
	var win=browser?window:Object; //非浏览器环境，Recorder挂载在Object下面
	var rec=win.Recorder,ni=rec.i18n;
	factory(rec,ni,ni.$T,browser);
}(function(Recorder,i18n,$T,isBrowser){
"use strict";

var ASR_Aliyun_Short=function(set){
	return new fn(set);
};
var ASR_Aliyun_ShortTxt="ASR_Aliyun_Short";
var fn=function(set){
	var This=this;
	var o={
		tokenApi:"" /*必填，调用阿里云一句话识别需要的token获取api地址
				接口实现请参考本地测试NodeJs后端程序：/assets/demo-asr/NodeJsServer_asr.aliyun.short.js
				此接口默认需要返回数据格式：
					{
						c:0 //code，0接口调用正常，其他数值接口调用出错
						,m:"" //message，接口调用出错时的错误消息
						,v:{ //value，接口成功调用返回的结果【结果中必须包含下面两个值】
							appkey:"aaaa" //lang语言模型对应的项目appkey
							,token:"bbbb" //语音识别Access Token
						}
					}
				如果不是返回的这个格式的数据，必须提供apiRequest配置，自行请求api*/
		,apiArgs:{ //请求tokenApi时要传的参数
			action:"token"
			,lang:"普通话" //语言模型设置（具体取值取决于tokenApi支持了哪些语言）
		}
		,apiRequest:null /*tokenApi的请求实现方法，默认使用简单的ajax实现
				如果你接口返回的数据格式和默认格式不一致，必须提供一个函数来自行请求api
				方法参数：fn(url,args,success,fail)
					url:"" == tokenApi
					args:{} == apiArgs
					success:fn(value) 接口调用成功回调，value={appkey:"", token:""}
					fail:fn(errMsg) 接口调用出错回调，errMsg="错误消息"
				*/
		,compatibleWebSocket:null /*提供一个函数返回兼容WebSocket的对象，一般也需要提供apiRequest
				如果你使用的环境不支持WebSocket，需要提供一个函数来返回一个兼容实现对象
				方法参数：fn(url) url为连接地址，返回一个对象，需支持的回调和方法：{
						onopen:fn() 连接成功回调
						onerror:fn({message}) 连接失败回调
						onclose:fn({code, reason}) 连接关闭回调
						onmessage:fn({data}) 收到消息回调
						connect:fn() 进行连接
						close:fn(code,reason) 关闭连接
						send:fn(data) 发送数据，data为字符串或者arraybuffer
					}
				binaryType固定使用arraybuffer类型
				*/
		
		//,asrProcess:null //fn(text,nextDuration,abortMsg) 当实时接收到语音识别结果时的回调函数（对单个完整音频文件的识别也有效）
				//此方法需要返回true才会继续识别，否则立即当做识别超时处理，你应当通过nextDuration来决定是否继续识别，避免无限制的识别大量消耗阿里云资源额度；如果不提供本回调，默认1分钟超时后终止识别(因为没有绑定回调，你不知道已经被终止了)
				//text为中间识别到的内容（并非已有录音片段的最终结果，后续可能会根据语境修整）
				//nextDuration 为当前回调时下次即将进行识别的总时长，单位毫秒，通过这个参数来限制识别总时长，超过时长就返回false终止识别（第二分钟开始每分钟会多识别前一分钟结尾的5秒数据，用于两分钟之间的拼接，相当于第二分钟最多识别55秒的新内容）
				//abortMsg如不为空代表识别中途因为某种原因终止了识别（比如超时、接口调用失败），收到此信息时应当立即调用asr的stop方法得到最终结果，并且终止录音
		
		,log:NOOP //fn(msg,color)提供一个日志输出接口，默认只会输出到控制台，color： 1:红色，2绿色，不为空时为颜色字符串
		
		//高级选项
		,fileSpeed:6 //单个文件识别发送速度控制，取值1-n；1：为按播放速率发送，最慢，识别精度完美；6：按六倍播放速度发送，花10秒识别60秒文件比较快，精度还行；再快测试发现似乎会缺失内容，可能是发送太快底层识别不过来导致返回的结果缺失。
	};
	for(var k in set){
		o[k]=set[k];
	};
	This.set=set=o;
	This.state=0;//0 未start，1 start，2 stop
	This.started=0;
	
	This.sampleRate=16000;//发送的采样率
	//This.tokenData
	
	This.pcmBuffers=[];//等待发送的缓冲数据
	This.pcmTotal=0;//输入的总量
	This.pcmOffset=0;//缓冲[0]的已发送位置
	This.pcmSend=0;//发送的总量，不会重复计算重发的量
	
	This.joinBuffers=[];//下一分钟左移5秒，和上一分钟重叠5秒
	This.joinSize=0;//左移的数据量
	This.joinSend=0;//单次已发送量
	This.joinOffset=-1;//左移[0]的已发送位置，-1代表可以进行整理buffers
	This.joinIsOpen=0;//是否开始发送
	This.joinSendTotal=0;//已发送重叠的总量
	
	This.sendCurSize=0;//单个wss发送量，不能超过1分钟的量
	This.sendTotal=0;//总计的发送量，存在重发重叠部分
	
	//This.stopWait=null 
	//This.sendWait=0
	//This.sendAbort=false
	//This.sendAbortMsg=""
	
	//This.wsCur 当前的wss
	//This.wsLock 新的一分钟wss准备
	This.resTxts=[];//每分钟结果列表 resTxt object: {tempTxt:"efg",okTxt:"efgh",fullTxt:"abcdefgh"}
	
	if(!set.asrProcess){
		This.log("未绑定asrProcess回调无法感知到abort事件",3);
	};
};
var CLog=function(){
	var v=arguments; v[0]="["+ASR_Aliyun_ShortTxt+"]"+v[0];
	Recorder.CLog.apply(null,v);
};
fn.prototype=ASR_Aliyun_Short.prototype={
	log:function(msg,color){
		CLog(msg,typeof color=="number"?color:0);
		this.set.log("["+ASR_Aliyun_ShortTxt+"]"+msg,color==3?"#f60":color);
	}
	
	
	//input已输入的音频数据总时长
	,inputDuration:function(){
		return Math.round(this.pcmTotal/this.sampleRate*1000);
	}
	//已发送识别的音频数据总时长，存在重发重叠部分，因此比inputDuration长
	,sendDuration:function(add){
		var size=this.sendTotal;
		size+=add||0;
		return Math.round(size/this.sampleRate*1000);
	}
	//已识别的音频数据总时长，去除了sendDuration的重叠部分，值<=inputDuration
	,asrDuration:function(){
		return this.sendDuration(-this.joinSendTotal);
	}
	
	
	/**一次性将单个完整音频文件转成文字，支持的文件类型由具体的浏览器决定，因此存在兼容性问题,兼容性mp3最好，wav次之，其他格式不一定能够解码。实际就是调用：浏览器解码音频得到PCM -> start -> input ... input -> stop
		blob:Blob 音频文件Blob对象，如：rec.stop得到的录音结果、file input选择的文件、XMLHttpRequest的blob结果、new Blob([TypedArray])创建的blob
		success fn(text,abortMsg) text为识别到的完整内容,abortMsg参考stop
		fail:fn(errMsg)
	**/
	,audioToText:function(blob,success,fail){
		var This=this;
		var failCall=function(err){
			This.log(err,1);
			fail&&fail(err);
		};
		if(!Recorder.GetContext()){//强制激活Recorder.Ctx 不支持大概率也不支持解码
			failCall("浏览器不支持音频解码");
			return;
		};
		
		var reader=new FileReader();
		reader.onloadend=function(){
			var ctx=Recorder.Ctx;
			ctx.decodeAudioData(reader.result,function(raw){
				var src=raw.getChannelData(0);
				var sampleRate=raw.sampleRate;
				
				var pcm=new Int16Array(src.length);
				for(var i=0;i<src.length;i++){//floatTo16BitPCM
					var s=Math.max(-1,Math.min(1,src[i]));
					s=s<0?s*0x8000:s*0x7FFF;
					pcm[i]=s;
				};
				
				This.pcmToText(pcm,sampleRate,success,fail);
			},function(e){
				failCall("音频解码失败["+blob.type+"]:"+e.message);
			});
		};
		reader.readAsArrayBuffer(blob);
	}
	/**一次性的将单个完整音频转成文字。实际就是调用:start -> input ... input -> stop
		buffer:[Int16,...] 16位单声道音频pcm数据，一维数组
		sampleRate pcm的采样率
		success fn(text,abortMsg) text为识别到的完整内容,abortMsg参考stop
		fail:fn(errMsg)
	**/
	,pcmToText:function(buffer,sampleRate,success,fail){
		var This=this;
		This.start(function(){
			This.log("单个文件"+Math.round(buffer.length/sampleRate*1000)+"ms转文字");
			This.sendSpeed=This.set.fileSpeed;
			This.input([buffer],sampleRate);
			This.stop(success,fail);
		},fail);
	}
	
	
	
	/**开始识别，开始后需要调用input输入录音数据，结束时调用stop来停止识别。如果start之前调用了input输入数据，这些数据将会等到start成功之后进行识别。
	建议在success回调中开始录音（即rec.start）；当然asr.start和rec.start同时进行调用，或者任意一个先调用都是允许的，不过当出现fail时，需要处理好asr和rec各自的状态。
	无需特殊处理start和stop的关系，只要调用了stop，会阻止未完成的start，不会执行回调。
		success:fn()
		fail:fn(errMsg)
	**/
	,start:function(success,fail){
		var This=this,set=This.set;
		var failCall=function(err){
			This.sendAbortMsg=err;
			fail&&fail(err);
		};
		if(!set.compatibleWebSocket){
			if(!isBrowser){
				failCall("非浏览器环境，请提供compatibleWebSocket配置来返回一个兼容的WebSocket");
				return;
			};
		};
		
		if(This.state!=0){
			failCall("ASR对象不可重复start");
			return;
		};
		This.state=1;
		
		var stopCancel=function(){
			This.log("ASR start被stop中断",1);
			This._send();//调用了再说，不管什么状态
		};
		This._token(function(){
			if(This.state!=1){
				stopCancel();
			}else{
				This.log("OK start",2);
				This.started=1;
				success&&success();
				
				This._send();//调用了再说，不管什么状态
			};
		},function(err){
			err="语音识别token接口出错："+err;
			This.log(err,1);
			if(This.state!=1){
				stopCancel();
			}else{
				failCall(err);
				This._send();//调用了再说，不管什么状态
			};
		});
	}
	/**结束识别，一般在调用了本方法后，下一行代码立即调用录音rec.stop结束录音
		success:fn(text,abortMsg) text为识别到的最终完整内容；如果存在abortMsg代表识别中途被某种错误停止了，text是停止前的内容识别到的完整内容，一般早在asrProcess中会收到abort事件然后要停止录音
		fail:fn(errMsg)
	**/
	,stop:function(success,fail){
		success=success||NOOP;
		fail=fail||NOOP;
		var This=this;
		var failCall=function(err){
			err="语音识别stop出错："+err;
			This.log(err,1);
			fail(err);
		};
		
		if(This.state==2){
			failCall("ASR对象不可重复stop");
			return;
		};
		This.state=2;
		
		This.stopWait=function(){
			This.stopWait=null;
			if(!This.started){
				fail(This.sendAbortMsg||"未开始语音识别");
				return;
			};
			var txt=This.getText();
			if(!txt && This.sendAbortMsg){
				fail(This.sendAbortMsg);//仅没有内容时，才走异常
			}else{
				success(txt, This.sendAbortMsg||"");//尽力返回已有内容
			};
		};
		//等待数据发送完
		This._send();
	}
	
	
	
	/**实时处理输入音频数据；不管有没有start，都可以调用本方法，start前输入的数据会缓冲起来等到start后进行识别
		buffers:[[Int16...],...] pcm片段列表，为二维数组，第一维数组内存放1个或多个pcm数据；比如可以是：rec.buffers、onProcess中的buffers截取的一段新二维数组
		sampleRate:48000 buffers中pcm的采样率
		
		buffersOffset:0 可选，默认0，从buffers第一维的这个位置开始识别，方便rec的onProcess中使用
	**/
	,input:function(buffers,sampleRate  ,buffersOffset){
		var This=this;
		
		if(This.state==2){//已停止，停止输入数据
			This._send();
			return;
		};
		var msg="input输入的采样率低于"+This.sampleRate;
		if(sampleRate<This.sampleRate){
			CLog(msg+"，数据已丢弃",3);
			if(!This.pcmTotal){
				This.sendAbortMsg=msg;
			};
			This._send();
			return;
		};
		if(This.sendAbortMsg==msg){
			This.sendAbortMsg="";
		};
		
		if(buffersOffset){
			var newBuffers=[];
			for(var idx=buffersOffset;idx<buffers.length;idx++){
				newBuffers.push(buffers[idx]);
			};
			buffers=newBuffers;
		};
		
		var pcm=Recorder.SampleData(buffers,sampleRate,This.sampleRate).data;
		This.pcmTotal+=pcm.length;
		This.pcmBuffers.push(pcm);
		This._send();
	}
	,_send:function(){
		var This=this,set=This.set;
		if(This.sendWait){
			//阻塞中
			return;
		};
		var tryStopEnd=function(){
			This.stopWait&&This.stopWait();
		};
		if(This.state==2 && (!This.started || !This.stopWait)){
			//已经stop了，并且未ok开始 或者 未在等待结果
			tryStopEnd();
			return;
		};
		if(This.sendAbort){
			//已异常中断了
			tryStopEnd();
			return;
		};
		
		//异常提前终止
		var abort=function(err){
			if(!This.sendAbort){
				This.sendAbort=1;
				This.sendAbortMsg=err||"-";
				processCall(0,1);//abort后只调用最后一次
			};
			This._send();
		};
		var processCall=function(addSize,abortLast){
			if(!abortLast && This.sendAbort){
				return false;
			};
			addSize=addSize||0;
			if(!set.asrProcess){
				//默认超过1分钟自动停止
				return This.sendTotal+addSize<=size60s;
			};
			//实时回调
			var val=set.asrProcess(This.getText()
				,This.sendDuration(addSize)
				,This.sendAbort?This.sendAbortMsg:"");
			if(!This._prsw && typeof(val)!="boolean"){
				CLog("asrProcess返回值必须是boolean类型，true才能继续识别，否则立即超时",1);
			};
			This._prsw=1;
			return val;
		};
		var size5s=This.sampleRate*5;
		var size60s=This.sampleRate*60;
		
		//建立ws连接
		var ws=This.wsCur;
		if(!ws){
			if(This.started){//已start才创建ws
				var resTxt={};
				This.resTxts.push(resTxt);
				ws=This.wsCur=This._wsNew(
					This.tokenData
					,"ws:"+This.resTxts.length
					,resTxt
					,function(){
						processCall();
					}
					,function(){
						This._send();
					}
					,function(err){
						//异常中断
						if(ws==This.wsCur){
							abort(err);
						};
					}
				);
			};
			return;
		};
		
		//正在新建新1分钟连接，等着
		if(This.wsLock){
			return;
		};
		//已有ok的连接，直接陆续将所有缓冲分段发送完
		if(ws._s!=2 || ws.isStop){
			//正在关闭或者其他状态不管，等着
			return;
		};
		//没有数据了
		if(This.pcmSend>=This.pcmTotal){
			if(This.state==1){
				//缓冲数据已发送完，等待新数据
				return;
			};
			
			//已stop，结束识别得到最终结果
			ws.stopWs(function(){
				tryStopEnd();
			},function(err){
				abort(err);
			});
			return;
		};
		
		//准备本次发送数据块
		var minSize=This.sampleRate/1000*50;//最小发送量50ms ≈1.6k
		var maxSize=This.sampleRate;//最大发送量1000ms ≈32k
		//速度控制1，取决于网速
		if((ws.bufferedAmount||0)/2>maxSize*3){
			//传输太慢，阻塞一会再发送
			This.sendWait=setTimeout(function(){
				This.sendWait=0;
				This._send();
			},100);
			return;
		};
		//速度控制2，取决于已发送时长，单个文件才会被控制速率
		if(This.sendSpeed){
			var spMaxMs=(Date.now()-ws.okTime)*This.sendSpeed;
			var nextMs=(This.sendCurSize+maxSize/3)/This.sampleRate*1000;
			var delay=Math.floor((nextMs-spMaxMs)/This.sendSpeed);
			if(delay>0){
				//传输太快，怕底层识别不过来，降低发送速度
				CLog("[ASR]延迟"+delay+"ms发送");
				This.sendWait=setTimeout(function(){
					This.sendWait=0;
					This._send();
				},delay);
				return;
			};
		};
		
		var needSend=1;
		var copyBuffers=function(offset,buffers,dist){
			var size=dist.length;
			for(var i=0,idx=0;idx<size&&i<buffers.length;){
				var pcm=buffers[i];
				if(pcm.length-offset<=size-idx){
					dist.set(offset==0?pcm:pcm.subarray(offset),idx);
					idx+=pcm.length-offset;
					offset=0;
					buffers.splice(i,1);
				}else{
					dist.set(pcm.subarray(offset,offset+(size-idx)),idx);
					offset+=size-idx;
					break;
				};
			};
			return offset;
		};
		if(This.joinIsOpen){
			//发送新1分钟的开头重叠5秒数据
			if(This.joinOffset==-1){
				//精准定位5秒
				This.joinSend=0;
				This.joinOffset=0;
				This.log("发送上1分钟结尾5秒数据...");
				var total=0;
				for(var i=This.joinBuffers.length-1;i>=0;i--){
					total+=This.joinBuffers[i].length;
					if(total>=size5s){
						This.joinBuffers.splice(0, i);
						This.joinSize=total;
						This.joinOffset=total-size5s;
						break;
					};
				};
			};
			var buffersSize=This.joinSize-This.joinOffset;//缓冲余量
			var size=Math.min(maxSize,buffersSize);
			if(size<=0){
				//重叠5秒数据发送完毕
				This.log("发送新1分钟数据(重叠"+Math.round(This.joinSend/This.sampleRate*1000)+"ms)...");
				This.joinBuffers=[];
				This.joinSize=0;
				This.joinOffset=-1;
				This.joinIsOpen=0;
				This._send();
				return;
			};
			
			//创建块数据，消耗掉buffers
			var chunk=new Int16Array(size);
			This.joinSend+=size;
			This.joinSendTotal+=size;
			This.joinOffset=copyBuffers(This.joinOffset,This.joinBuffers,chunk);
			
			This.joinSize=0;
			for(var i=0;i<This.joinBuffers.length;i++){
				This.joinSize+=This.joinBuffers[i].length;
			};
		}else{
			var buffersSize=This.pcmTotal-This.pcmSend;//缓冲余量
			var buffersDur=Math.round(buffersSize/This.sampleRate*1000);
			var curHasSize=size60s-This.sendCurSize;//当前连接剩余能发送的量
			var sizeNext=Math.min(maxSize,buffersSize);//不管连接剩余数时本应当发送的数量
			var size=Math.min(sizeNext,curHasSize);
			if(This.state==1 && size<Math.min(minSize,curHasSize)){
				//不够发送一次的，等待新数据
				return;
			};
			var needNew=0;
			if(curHasSize<=0){
				//当前连接一分钟已消耗完
				if(This.state==2 && buffersSize<This.sampleRate*1.2){
					//剩余的量太少，并且已stop，没必要再新建连接，直接丢弃
					size=buffersSize;
					This.log("丢弃结尾"+buffersDur+"ms数据","#999");
					needSend=0;
				}else{
					//开始新1分钟的连接，等到实时回调后再看要不要新建
					needNew=true;
				};
			};
			//回调看看是否要超时终止掉
			if(needSend && !processCall(sizeNext)){//用本应当的发送量来计算
				//超时，终止识别
				var durS=Math.round(This.asrDuration()/1000);
				This.log("已主动超时，共识别"+durS+"秒，丢弃缓冲"+buffersDur+"ms，正在终止...");
				This.wsLock=1;//阻塞住后续调用
				ws.stopWs(function(){
					abort("已主动超时，共识别"+durS+"秒，终止识别");
				},function(err){
					abort(err);
				});
				return;
			};
			//开始新1分钟的连接
			if(needNew){
				CLog("[ASR]新1分钟接续，当前缓冲"+buffersDur+"ms...");
				This.wsLock=1;//阻塞住后续调用
				ws.stopWs(function(){
					This._token(function(){
						This.log("新1分钟接续OK，当前缓冲"+buffersDur+"ms",2);
						This.wsLock=0;
						This.wsCur=0;//重置当前连接
						This.sendCurSize=0;
						
						This.joinIsOpen=1;//新1分钟先发重叠的5秒数据
						This.joinOffset=-1;
						
						This._send();
					},function(err){
						abort("语音识别新1分钟token接口出错："+err);
					});
				},function(err){
					abort(err);
				});
				return;
			};
			
			//创建块数据，消耗掉buffers
			var chunk=new Int16Array(size);
			This.pcmOffset=copyBuffers(This.pcmOffset,This.pcmBuffers,chunk);
			This.pcmSend+=size;
			
			//写入到下一分钟的头5秒重叠区域中，不管写了多少，写就完了
			This.joinBuffers.push(chunk);
			This.joinSize+=size;
		};
		
		This.sendCurSize+=chunk.length;
		This.sendTotal+=chunk.length;
		if(needSend){
			try{
				ws.send(chunk.buffer);
			}catch(e){CLog("ws.send",1,e);};
		};
		
		//不要停
		This.sendWait=setTimeout(function(){
			This.sendWait=0;
			This._send();
		});//仅退出调用堆栈
	}
	
	
	
	/**返回实时结果文本，如果已stop返回的就是最终文本**/
	,getText:function(){
		var arr=this.resTxts;
		var txt="";
		for(var i=0;i<arr.length;i++){
			var obj=arr[i];
			if(obj.fullTxt){
				txt=obj.fullTxt;
			}else{
				var tmp=obj.tempTxt||"";
				if(obj.okTxt){
					tmp=obj.okTxt;
				};
				//5秒重叠进行模糊拼接
				if(!txt){
					txt=tmp;
				}else{
					var left=txt.substr(-20);//240字/分
					var finds=[];
					for(var x=0,max=Math.min(17,tmp.length-3);x<=max;x++){
						for(var i0=0;i0<17;i0++){
							if(left[i0]==tmp[x]){
								var n=1;
								for(;n<17;n++){
									if(left[i0+n]!=tmp[x+n]){
										break;
									};
								};
								if(n>=3){//3字相同即匹配
									finds.push({x:x,i0:i0,n:n});
								};
							};
						};
					};
					finds.sort(function(a,b){
						var v=b.n-a.n;
						return v!=0?v:b.i0-a.i0;//越长越好，越靠后越好
					});
					var f0=finds[0];
					if(f0){
						txt=txt.substr(0,txt.length-left.length+f0.i0);
						txt+=tmp.substr(f0.x);
					}else{
						txt+=tmp;
					};
				};
				//存起来
				if(obj.okTxt!=null && tmp==obj.okTxt){
					obj.fullTxt=txt;
				};
			};
		};
		return txt;
	}
	
	//创建新的wss连接
	,_wsNew:function(sData,id,resTxt,process,connOk,connFail){
		var uuid=function(){
			var s=[];
			for(var i=0,r;i<32;i++){
				r=Math.floor(Math.random()*16);
				s.push(String.fromCharCode(r<10?r+48:r-10+97));
			};
			return s.join("");
		};
		var This=this,set=This.set;
		CLog("[ASR "+id+"]正在连接...");
		var url="wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1?token="+sData.token;
		if(set.compatibleWebSocket){
			var ws=set.compatibleWebSocket(url);
		}else{
			var ws=new WebSocket(url);
		}
		
		//ws._s=0 0连接中 1opening 2openOK 3stoping 4closeing -1closed
		//ws.isStop=0 1已停止识别
		ws.onclose=function(){
			if(ws._s==-1)return;
			var isFail=ws._s!=4;
			ws._s=-1;
			This.log("["+id+"]close");
			
			isFail&&connFail(ws._err||"连接"+id+"已关闭");
		};
		ws.onerror=function(e){
			if(ws._s==-1)return;
			var msg="网络连接错误";
			ws._err||(ws._err=msg);
			This.log("["+id+"]"+msg,1);
			ws.onclose();
		};
		ws.onopen=function(){
			if(ws._s==-1)return;
			ws._s=1;
			CLog("[ASR "+id+"]open");
			ws._task=uuid();
			ws.send(JSON.stringify({
				header:{
					message_id:uuid()
					,task_id:ws._task
					,appkey:sData.appkey
					
					,namespace:"SpeechRecognizer"
					,name:"StartRecognition"
				}
				,payload:{
					format:"pcm"
					,sample_rate:This.sampleRate
					,enable_intermediate_result:true //返回中间识别结果
					,enable_punctuation_prediction:true //添加标点
					,enable_inverse_text_normalization:true //后处理中将数值处理
				}
				,context:{ }
			}));
		};
		ws.onmessage=function(e){
			var data=e.data;
			var logMsg=true;
			if(typeof(data)=="string" && data[0]=="{"){
				data=JSON.parse(data);
				var header=data.header||{};
				var payload=data.payload||{};
				var name=header.name||"";
				var status=header.status||0;
				
				var isFail=name=="TaskFailed";
				var errMsg="";
				
				//init
				if(ws._s==1 && (name=="RecognitionStarted" || isFail)){
					if(isFail){
						errMsg="连接"+id+"失败["+status+"]"+header.status_text;
					}else{
						ws._s=2;
						This.log("["+id+"]连接OK");
						ws.okTime=Date.now();
						connOk();
					};
				};
				//中间结果
				if(ws._s==2 && (name=="RecognitionResultChanged" || isFail)){
					if(isFail){
						errMsg="识别出现错误["+status+"]"+header.status_text;
					}else{
						logMsg=!ws._clmsg;
						ws._clmsg=1;
						resTxt.tempTxt=payload.result||"";
						process();
					};
				};
				//stop
				if(ws._s==3 && (name=="RecognitionCompleted" || isFail)){
					var txt="";
					if(isFail){
						errMsg="停止识别出现错误["+status+"]"+header.status_text;
					}else{
						txt=payload.result||"";
						This.log("["+id+"]最终识别结果："+txt);
					};
					ws.stopCall&&ws.stopCall(txt,errMsg);
				};
				
				if(errMsg){
					This.log("["+id+"]"+errMsg,1);
					ws._err||(ws._err=errMsg);
				};
			};
			if(logMsg){
				CLog("[ASR "+id+"]msg",data);
			};
		};
		ws.stopWs=function(True,False){
			if(ws._s!=2){
				False(id+"状态不正确["+ws._s+"]");
				return;
			};
			ws._s=3;
			ws.isStop=1;
			
			ws.stopCall=function(txt,err){
				clearTimeout(ws.stopInt);
				ws.stopCall=0;
				ws._s=4;
				ws.close();
				
				resTxt.okTxt=txt;
				process();
				
				if(err){
					False(err);
				}else{
					True();
				};
			};
			ws.stopInt=setTimeout(function(){
				ws.stopCall&&ws.stopCall("","停止识别返回结果超时");
			},10000);
			
			CLog("[ASR "+id+"]send stop");
			ws.send(JSON.stringify({
				header:{
					message_id:uuid()
					,task_id:ws._task
					,appkey:sData.appkey
					
					,namespace:"SpeechRecognizer"
					,name:"StopRecognition"
				}
			}));
		};
		if(ws.connect)ws.connect(); //兼容时会有这个方法
		return ws;
	}
	
	
	
	//获得开始识别的token信息
	,_token:function(True,False){
		var This=this,set=This.set;
		if(!set.tokenApi){
			False("未配置tokenApi");return;
		};
		
		(set.apiRequest||DefaultPost)(set.tokenApi,set.apiArgs||{},function(data){
			if(!data || !data.appkey || !data.token){
				False("apiRequest回调的数据格式不正确");return;
			};
			This.tokenData=data;
			True();
		},False);
	}
	
};



//手撸一个ajax
function DefaultPost(url,args,success,fail){
	var xhr=new XMLHttpRequest();
	xhr.timeout=20000;
	xhr.open("POST",url);
	xhr.onreadystatechange=function(){
		if(xhr.readyState==4){
			if(xhr.status==200){
				try{
					var o=JSON.parse(xhr.responseText);
				}catch(e){};
				
				if(o.c!==0 || !o.v){
					fail(o.m||"接口返回非预定义json数据");
					return;
				};
				success(o.v);
			}else{
				fail("请求失败["+xhr.status+"]");
			}
		}
	};
	var arr=[];
	for(var k in args){
		arr.push(k+"="+encodeURIComponent(args[k]));
	};
	xhr.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
	xhr.send(arr.join("&"));
};

function NOOP(){};

Recorder[ASR_Aliyun_ShortTxt]=ASR_Aliyun_Short;

	
}));