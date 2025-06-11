/*
录音 Recorder扩展，实时播放录音片段文件，把片段文件转换成MediaStream流

https://github.com/xiangyuecn/Recorder

BufferStreamPlayer可以通过input方法一次性输入整个音频文件，或者实时输入音频片段文件，然后播放出来；输入支持格式：pcm、wav、mp3等浏览器支持的音频格式，非pcm格式会自动解码成pcm（播放音质效果比pcm、wav格式差点）；输入前输入后都可进行处理要播放的音频，比如：混音、变速、变调；输入的音频会写入到内部的MediaStream流中，完成将连续的音频片段文件转换成流。

BufferStreamPlayer可以用于：
	1. Recorder onProcess等实时处理中，将实时处理好的音频片段转直接换成MediaStream，此流可以作为WebRTC的local流发送到对方，或播放出来；
	2. 接收到的音频片段文件的实时播放，比如：WebSocket接收到的录音片段文件播放、WebRTC remote流（Recorder支持对这种流进行实时处理）实时处理后的播放；
	3. 单个音频文件的实时播放处理，比如：播放一段音频，并同时进行可视化绘制（其实自己解码+播放绘制比直接调用这个更有趣，但这个省事、配套功能多点）。

在线测试例子：
	https://xiangyuecn.github.io/Recorder/assets/工具-代码运行和静态分发Runtime.html?jsname=teach.realtime.decode_buffer_stream_player
调用示例：
	var stream=Recorder.BufferStreamPlayer(set)
	//创建好后第一件事就是start打开流，打开后就会开始播放input输入的音频，set具体配置看下面源码；注意：start需要在用户操作(触摸、点击等)时进行调用，原因参考runningContext配置
	stream.start(()=>{
		stream.currentTime;//当前已播放的时长，单位ms，数值变化时会有onUpdateTime事件
		stream.duration;//已输入的全部数据总时长，单位ms，数值变化时会有onUpdateTime事件；实时模式下意义不大，会比实际播放的长，因为实时播放时卡了就会丢弃部分数据不播放
		stream.isStop;//是否已停止，调用了stop方法时会设为true
		stream.isPause;//是否已暂停，调用了pause方法时会设为true
		stream.isPlayEnd;//已输入的数据是否播放到了结尾（没有可播放的数据了），input后又会变成false；可代表正在缓冲中或播放结束，状态变更时会有onPlayEnd事件
		
		//如果不要默认的播放，可以设置set.play为false，这种情况下只拿到MediaStream来用
		stream.getMediaStream() //通过getMediaStream方法得到MediaStream流，此流可以作为WebRTC的local流发送到对方，或者直接拿来赋值给audio.srcObject来播放（和赋值audio.src作用一致）；未start时调用此方法将会抛异常
		
		stream.getAudioSrc() //【已过时】超低版本浏览器中得到MediaStream流的字符串播放地址，可赋值给audio标签的src，直接播放音频；未start时调用此方法将会抛异常；新版本浏览器已停止支持将MediaStream转换成url字符串，调用本方法新浏览器会抛异常，因此在不需要兼容不支持srcObject的超低版本浏览器时，请直接使用getMediaStream然后赋值给auido.srcObject来播放
	},(errMsg)=>{
		//start失败，无法播放
	});

	//随时都能调用input，会等到start成功后播放出来，不停的调用input，就能持续的播放出声音了，需要暂停播放就不要调用input就行了
	stream.input(anyData); //anyData数据格式 和更多说明，请阅读下面的input方法源码注释
	stream.clearInput(keepDuration); //清除已输入但还未播放的数据，一般用于非实时模式打断老的播放；返回清除的音频时长，默认会从总时长duration中减去此时长，keepDuration=true时不减去
	
	//暂停播放，暂停后：实时模式下会丢弃所有input输入的数据（resume时只播放新input的数据），非实时模式下所有input输入的数据会保留到resume时继续播放
	stream.pause();
	//恢复播放，实时模式下只会从最新input的数据开始播放，非实时模式下会从暂停的位置继续播放
	stream.resume();

	//不要播放了就调用stop停止播放，关闭所有资源
	stream.stop();
	


注意：已知Firefox的AudioBuffer没法动态修改数据，所以对于带有这种特性的浏览器将采用先缓冲后再播放（类似assets/runtime-codes/fragment.playbuffer.js），音质会相对差一点；其他浏览器测试Android、IOS、Chrome无此问题；start方法中有一大段代码给浏览器做了特性检测并进行兼容处理。
*/
(function(factory){
	var browser=typeof window=="object" && !!window.document;
	var win=browser?window:Object; //非浏览器环境，Recorder挂载在Object下面
	var rec=win.Recorder,ni=rec.i18n;
	factory(rec,ni,ni.$T,browser);
}(function(Recorder,i18n,$T,isBrowser){
"use strict";

var BufferStreamPlayer=function(set){
	return new fn(set);
};
var BufferStreamPlayerTxt="BufferStreamPlayer";
var fn=function(set){
	var This=this;
	var o={
		play:true //要播放声音，设为false不播放，只提供MediaStream
		,realtime:true /*默认为true实时模式，设为false为非实时模式
			实时模式：设为 true 或 {maxDelay:300,discardAll:false}配置对象
				如果有新的input输入数据，但之前输入的数据还未播放完的时长不超过maxDelay时（缓冲播放延迟默认限制在300ms内），如果积压的数据量过大则积压的数据将会被直接丢弃，少量积压会和新数据一起加速播放，最终达到尽快播放新输入的数据的目的；这在网络不流畅卡顿时会发挥很大作用，可有效降低播放延迟；出现加速播放时声音听起来会比较怪异，可配置discardAll=true来关闭此特性，少量积压的数据也直接丢弃，不会加速播放；如果你的音频数据块超过200ms，需要调大maxDelay（取值100-800ms）
			非实时模式：设为 false
				连续完整的播放完所有input输入的数据，之前输入的还未播放完又有新input输入会加入队列排队播放，比如用于：一次性同时输入几段音频完整播放
			*/
				
		
		//,onInputError:fn(errMsg, inputIndex) //当input输入出错时回调，参数为input第几次调用和错误消息
		//,onUpdateTime:fn() //已播放时长、总时长更新回调（stop、pause、resume后一定会回调），this.currentTime为已播放时长，this.duration为已输入的全部数据总时长（实时模式下意义不大，会比实际播放的长），单位都是ms
		//,onPlayEnd:fn() //没有可播放的数据时回调（stop后一定会回调），已输入的数据已全部播放完了，可代表正在缓冲中或播放结束；之后如果继续input输入了新数据，播放完后会再次回调，因此会多次回调；非实时模式一次性输入了数据时，此回调相当于播放完成，可以stop掉，重新创建对象来input数据可达到循环播放效果
		
		//,decode:false //input输入的数据在调用transform之前是否要进行一次音频解码成pcm [Int16,...]
			//mp3、wav等都可以设为true、或设为{fadeInOut:true}配置对象，会自动解码成pcm；默认会开启fadeInOut对解码的pcm首尾进行淡入淡出处理，减少爆音（wav等解码后和原始pcm一致的音频，可以把fadeInOut设为false）
		
		//transform:fn(inputData,sampleRate,True,False)
			//将input输入的data（如果开启了decode将是解码后的pcm）转换处理成要播放的pcm数据；如果没有解码也没有提供本方法，input的data必须是[Int16,...]并且设置set.sampleRate
			//inputData:any input方法输入的任意格式数据，只要这个转换函数支持处理；如果开启了decode，此数据为input输入的数据解码后的pcm [Int16,...]
			//sampleRate:123 如果设置了decode为解码后的采样率，否则为set.sampleRate || null
			//True(pcm,sampleRate) 回调处理好的pcm数据([Int16,...])和pcm的采样率
			//False(errMsg) 处理失败回调
			
		//sampleRate:16000 //可选input输入的数据默认的采样率，当没有设置解码也没有提供transform时应当明确设置采样率
		
		//runningContext:AudioContext //可选提供一个state为running状态的AudioContext对象(ctx)，默认会在start时自动创建一个新的ctx，这个配置的作用请参阅Recorder的runningContext配置
	};
	for(var k in set){
		o[k]=set[k];
	};
	This.set=set=o;
	
	if(!set.onInputError){
		set.onInputError=function(err,n){ CLog(err,1); };
	}
};
fn.prototype=BufferStreamPlayer.prototype={
	/**【已过时】获取MediaStream的audio播放地址，新版浏览器、未start将会抛异常**/
	getAudioSrc:function(){
		CLog($T("0XYC::getAudioSrc方法已过时：请直接使用getMediaStream然后赋值给audio.srcObject，仅允许在不支持srcObject的浏览器中调用本方法赋值给audio.src以做兼容"),3);
		if(!this._src){
			//新版chrome调用createObjectURL会直接抛异常了 https://developer.mozilla.org/en-US/docs/Web/API/URL/createObjectURL#using_object_urls_for_media_streams
			this._src=(window.URL||webkitURL).createObjectURL(this.getMediaStream());
		}
		return this._src;
	}
	/**获取MediaStream流对象，未start将会抛异常**/
	,getMediaStream:function(){
		if(!this._dest){
			throw new Error(NoStartMsg());
		}
		return this._dest.stream;
	}
	
	
	/**打开音频流，打开后就会开始播放input输入的音频；注意：start需要在用户操作(触摸、点击等)时进行调用，原因参考runningContext配置
	 * True() 打开成功回调
	 * False(errMsg) 打开失败回调**/
	,start:function(True,False){
		var falseCall=function(msg,noClear){
			var next=!checkStop();
			if(!noClear)This._clear();
			CLog(msg,1);
			next&&False&&False(msg);
		};
		var checkStop=function(){
			if(This.isStop){
				CLog($T("6DDt::start被stop终止"),3);
				return true;
			};
		};
		var This=this,set=This.set,__abTest=This.__abTest;
		if(This._Tc!=null){
			falseCall($T("I4h4::{1}多次start",0,BufferStreamPlayerTxt),1);
			return;
		}
		if(!isBrowser){
			falseCall($T.G("NonBrowser-1",[BufferStreamPlayerTxt]));
			return;
		}
		This._Tc=0;//currentTime 对应的采样数
		This._Td=0;//duration 对应的采样数
		
		This.currentTime=0;//当前已播放的时长，单位ms
		This.duration=0;//已输入的全部数据总时长，单位ms；实时模式下意义不大，会比实际播放的长，因为实时播放时卡了就会丢弃部分数据不播放
		This.isStop=0;//是否已停止
		This.isPause=0;//是否已暂停
		This.isPlayEnd=0;//已输入的数据是否播放到了结尾（没有可播放的数据了），input后又会变成false；可代表正在缓冲中或播放结束
		
		This.inputN=0;//第n次调用input
		
		This.inputQueueIdx=0;//input调用队列当前已处理到的位置
		This.inputQueue=[];//input调用队列，用于纠正执行顺序
		
		This.bufferSampleRate=0;//audioBuffer的采样率，首次input后就会固定下来
		This.audioBuffer=0;
		This.pcmBuffer=[[],[]];//未推入audioBuffer的pcm数据缓冲
		
		var fail=function(msg){
			falseCall($T("P6Gs::浏览器不支持打开{1}",0,BufferStreamPlayerTxt)+(msg?": "+msg:""));
		};
		
		var ctx=set.runningContext || Recorder.GetContext(true); This._ctx=ctx;
		var sVal=ctx.state,spEnd=Recorder.CtxSpEnd(sVal);
		!__abTest&&CLog("start... ctx.state="+sVal+(
			spEnd?$T("JwDm::（注意：ctx不是running状态，start需要在用户操作(触摸、点击等)时进行调用，否则会尝试进行ctx.resume，可能会产生兼容性问题(仅iOS)，请参阅文档中runningContext配置）"):""
		));
		
		var support=1;
		if(!ctx || !ctx.createMediaStreamDestination){
			support=0;
		}else{
			var source=ctx.createBufferSource();
			if(!source.start || source.onended===undefined){
				support=0;//createBufferSource版本太低，难兼容
			}
		};
		if(!support){
			fail("");
			return;
		};
		
		
		var end=function(){
			if(checkStop())return;
			//创建MediaStream
			var dest=ctx.createMediaStreamDestination();
			dest.channelCount=1;
			This._dest=dest;
			
			!__abTest&&CLog("start ok");
			True&&True();
			
			This._inputProcess();//处理未完成start前的input调用
			This._updateTime();//更新时间
			
			//定时在没有input输入时，将未写入buffer的数据写进去
			if(!badAB){
				This._writeInt=setInterval(function(){
					This._writeBuffer();
				},100);
			}else{
				CLog($T("qx6X::此浏览器的AudioBuffer实现不支持动态特性，采用兼容模式"),3);
				This._writeInt=setInterval(function(){
					This._writeBad();
				},10);//定时调用进行数据写入播放
			}
		};
		var abTest=function(){
			//浏览器实现检测，已知Firefox的AudioBuffer没法在_writeBuffer中动态修改数据；检测方法：直接新开一个，输入一段测试数据，看看能不能拿到流中的数据
			var testStream=BufferStreamPlayer({ play:false,sampleRate:8000,runningContext:ctx });
			testStream.__abTest=1; var testRec;
			testStream.start(function(){
				testRec=Recorder({
					type:"unknown"
					,sourceStream:testStream.getMediaStream()
					,runningContext:ctx
					,onProcess:function(buffers){	
						var bf=buffers[buffers.length-1],all0=1;
						for(var i=0;i<bf.length;i++){
							if(bf[i]!=0){ all0=0; break; }
						}
						if(all0 && buffers.length<5){
							return;//再等等看，最长约等500ms
						}
						testRec.close();
						testStream.stop();
						
						if(testInt){ clearTimeout(testInt); testInt=0;
							//全部是0就是浏览器不行，要缓冲一次性播放进行兼容
							badAB=all0;
							BufferStreamPlayer.BadAudioBuffer=badAB;
							end();
						}
					}
				});
				testRec.open(function(){
					testRec.start();
				},function(msg){
					testStream.stop(); fail(msg);
				});
			},fail);
			//超时没有回调
			var testInt=setTimeout(function(){
				testInt=0; testStream.stop(); testRec&&testRec.close();
				fail($T("cdOx::环境检测超时"));
			},1500);
			//随机生成1秒的数据，rec有一次回调即可
			var data=new Int16Array(8000);
			for(var i=0;i<8000;i++){
				data[i]=~~(Math.random()*0x7fff*2-0x7fff);
			}
			testStream.input(data);
		};
		
		var badAB=BufferStreamPlayer.BadAudioBuffer;
		var ctxNext=function(){
			if(__abTest || badAB!=null){
				setTimeout(end); //应当setTimeout一下强转成异步，统一调用代码时的行为
			}else{
				abTest();
			};
		};
		var tag="AudioContext resume: ";
		Recorder.ResumeCtx(ctx,function(runC){
			runC&&CLog(tag+"wait...");
			return !This.isStop;
		},function(runC){
			runC&&CLog(tag+ctx.state);
			ctxNext();
		},function(err){ //比较少见，可能没有影响
			CLog(tag+ctx.state+" "+$T("S2Bu::可能无法播放：{1}",0,err),1);
			ctxNext();
		});
	}
	,_clear:function(){
		var This=this;
		This.isStop=1;
		clearInterval(This._writeInt);
		This.inputQueue=0;
		
		if(This._src){
			(window.URL||webkitURL).revokeObjectURL(This._src);
			This._src=0;
		}
		if(This._dest){
			Recorder.StopS_(This._dest.stream);
			This._dest=0;
		}
		if(!This.set.runningContext && This._ctx){
			Recorder.CloseNewCtx(This._ctx);
		}
		This._ctx=0;
		
		var source=This.bufferSource;
		if(source){
			source.disconnect();
			source.stop();
		}
		This.bufferSource=0;
		This.audioBuffer=0;
	}
	/**停止播放，关闭所有资源**/
	,stop:function(){
		var This=this;
		This._clear();
		
		!This.__abTest&&CLog("stop");
		This._playEnd(1);
	}
	/**暂停播放，暂停后：实时模式下会丢弃所有input输入的数据（resume时只播放新input的数据），非实时模式下所有input输入的数据会保留到resume时继续播放**/
	,pause:function(){
		CLog("pause");
		this.isPause=1;
		this._updateTime(1);
	}
	/**恢复播放，实时模式下只会从最新input的数据开始播放，非实时模式下会从暂停的位置继续播放**/
	,resume:function(){
		var This=this,tag="resume",tag3=tag+"(wait ctx)";
		CLog(tag);
		This.isPause=0;
		This._updateTime(1);
		
		var ctx=This._ctx;
		if(ctx){ //AudioContext如果被暂停，尽量恢复
			Recorder.ResumeCtx(ctx,function(runC){
				runC&&CLog(tag3+"...");
				return !This.isStop && !This.isPause;
			},function(runC){
				runC&&CLog(tag3+ctx.state);
			},function(err){
				CLog(tag3+ctx.state+"[err]"+err,1);
			});
		};
	}
	
	
	//当前输入的数据播放到结尾时触发回调，stop时永远会触发回调
	,_playEnd:function(stop){
		var This=this,startTime=This._PNs,call=This.set.onPlayEnd;
		if(stop || !This.isPause){//暂停播到结尾不算
			if(stop || !This.isPlayEnd){
				if(stop || (startTime && Date.now()-startTime>500)){//已停止或者延迟确认成功
					This._PNs=0;
					This.isPlayEnd=1;
					call&&call();
					This._updateTime(1);
				}else if(!startTime){//刚检测到的没有数据了，开始延迟确认
					This._PNs=Date.now();
				};
			};
		};
	}
	//有数据播放时，取消已到结尾状态
	,_playLive:function(){
		var This=this;
		This.isPlayEnd=0;
		This._PNs=0;
	}
	//时间更新时触发回调，没有更新时不会触发回调
	,_updateTime:function(must){
		var This=this,sampleRate=This.bufferSampleRate||9e9,call=This.set.onUpdateTime;
		This.currentTime=Math.round(This._Tc/sampleRate*1000);
		This.duration=Math.round(This._Td/sampleRate*1000);
		
		var s=""+This.currentTime+This.duration;
		if(must || This._UTs!=s){
			This._UTs=s;
			call&&call();
		}
	}
	
	
	
	
	
	/**输入任意格式的音频数据，未完成start前调用会等到start成功后生效
		anyData: any 具体类型取决于：
			set.decode为false时:
				未提供set.transform，数据必须是pcm[Int16,...]，此时的set必须提供sampleRate；
				提供了set.transform，数据为transform方法支持的任意格式。
			set.decode为true时:
				数据必须是ArrayBuffer，会自动解码成pcm[Int16,...]；注意输入的每一片数据都应该是完整的一个音频片段文件，否则可能会解码失败；注意ArrayBuffer对象是Transferable object，参与解码后此对象将不可用，因为内存数据已被转移到了解码线程，可通过 stream.input(arrayBuffer.slice(0)) 形式复制一份再解码就没有这个问题了。
				
		关于anyData的二进制长度：
			如果是提供的pcm、wav格式数据，数据长度对播放无太大影响，很短的数据也能很好的连续播放。
			如果是提供的mp3这种必须解码才能获得pcm的数据，数据应当尽量长点，测试发现片段有300ms以上解码后能很好的连续播放，低于100ms解码后可能会有明显的杂音，更低的可能会解码失败；当片段确实太小时，可以将本来会多次input调用的数据缓冲起来，等数据量达到了300ms再来调用一次input，能比较显著的改善播放音质。
	 **/
	,input:function(anyData){
		var This=this,set=This.set;
		var inputN=++This.inputN;
		if(!This.inputQueue){
			throw new Error(NoStartMsg());
		}
		
		var decSet=set.decode;
		if(decSet){
			//先解码
			DecodeAudio(anyData, function(data){
				if(!This.inputQueue)return;//stop了
				if(decSet.fadeInOut==null || decSet.fadeInOut){
					FadeInOut(data.data, data.sampleRate);//解码后的数据进行一下淡入淡出处理，减少爆音
				}
				This._input2(inputN, data.data, data.sampleRate);
			},function(err){
				This._inputErr(err, inputN);
			});
		}else{
			This._input2(inputN, anyData, set.sampleRate);
		}
	}
	//transform处理
	,_input2:function(inputN, anyData, sampleRate){
		var This=this,set=This.set;
		
		if(set.transform){
			set.transform(anyData, sampleRate, function(pcm, sampleRate2){
				if(!This.inputQueue)return;//stop了
				
				sampleRate=sampleRate2||sampleRate;
				This._input3(inputN, pcm, sampleRate);
			},function(err){
				This._inputErr(err, inputN);
			});
		}else{
			This._input3(inputN, anyData, sampleRate);
		}
	}
	//转换好的pcm加入input队列，纠正调用顺序，未start时等待
	,_input3:function(inputN, pcm, sampleRate){
		var This=this;
		
		if(!pcm || !pcm.subarray){
			This._inputErr($T("ZfGG::input调用失败：非pcm[Int16,...]输入时，必须解码或者使用transform转换"), inputN);
			return;
		}
		if(!sampleRate){
			This._inputErr($T("N4ke::input调用失败：未提供sampleRate"), inputN);
			return;
		}
		if(This.bufferSampleRate && This.bufferSampleRate!=sampleRate){
			This._inputErr($T("IHZd::input调用失败：data的sampleRate={1}和之前的={2}不同",0,sampleRate,This.bufferSampleRate), inputN);
			return;
		}
		if(!This.bufferSampleRate){
			This.bufferSampleRate=sampleRate;//首次处理后，固定下来，后续的每次输入都是相同的
		}
		
		//加入队列，纠正input执行顺序，解码、transform均有可能会导致顺序不一致
		if(inputN>This.inputQueueIdx){ //clearInput移动了队列位置的丢弃
			This.inputQueue[inputN]=pcm;
		}
		
		if(This._dest){//已start，可以开始处理队列
			This._inputProcess();
		}
	}
	,_inputErr:function(errMsg, inputN){
		if(!this.inputQueue) return;//stop了
		this.inputQueue[inputN]=1;//出错了，队列里面也要占个位
		this.set.onInputError(errMsg, inputN);
	}
	//处理input队列
	,_inputProcess:function(){
		var This=this;
		if(!This.bufferSampleRate){
			return;
		}
		
		var queue=This.inputQueue;
		for(var i=This.inputQueueIdx+1;i<queue.length;i++){ //inputN是从1开始，所以+1
			var pcm=queue[i];
			if(pcm==1){
				This.inputQueueIdx=i;//跳过出错的input
				continue;
			}
			if(!pcm){
				return;//之前的input还未进入本方法，退出等待
			}
			
			This.inputQueueIdx=i;
			queue[i]=null;
			
			//推入缓冲，最多两个元素 [堆积的，新的]
			var pcms=This.pcmBuffer;
			var pcm0=pcms[0],pcm1=pcms[1];
			if(pcm0.length){
				if(pcm1.length){
					var tmp=new Int16Array(pcm0.length+pcm1.length);
					tmp.set(pcm0);
					tmp.set(pcm1,pcm0.length);
					pcms[0]=tmp;
				}
			}else{
				pcms[0]=pcm1;
			}
			pcms[1]=pcm;
			
			This._Td+=pcm.length;//更新已输入总时长
			This._updateTime();
			This._playLive();//有播放数据了
		}
		
		if(!BufferStreamPlayer.BadAudioBuffer){
			if(!This.audioBuffer){
				This._createBuffer(true);
			}else{
				This._writeBuffer();
			}
		}else{
			This._writeBad();
		}
	}
	
	/**清除已输入但还未播放的数据，一般用于非实时模式打断老的播放；返回清除的音频时长，默认会从总时长duration中减去此时长，keepDuration时不减去*/
	,clearInput:function(keepDuration){
		var This=this, sampleRate=This.bufferSampleRate, size=0;
		if(This.inputQueue){//未stop
			This.inputQueueIdx=This.inputN;//队列位置移到结尾
			
			var pcms=This.pcmBuffer;
			size=pcms[0].length+pcms[1].length;
			This._subClear();
			if(!keepDuration) This._Td-=size;//减掉已输入总时长
			This._updateTime(1);
		}
		var dur = size? Math.round(size/sampleRate*1000) : 0;
		CLog("clearInput "+dur+"ms "+size);
		return dur;
	}
	
	
	
	
	
	
	/****************正常的播放处理****************/
	//创建播放buffer
	,_createBuffer:function(init){
		var This=this,set=This.set;
		if(!init && !This.audioBuffer){
			return;
		}
		
		var ctx=This._ctx;
		var sampleRate=This.bufferSampleRate;
		var bufferSize=sampleRate*(set.bufferSecond||60);//建一个可以持续播放60秒的buffer，循环写入数据播放，大点好简单省事
		var buffer=ctx.createBuffer(1, bufferSize,sampleRate);
		
		var source=ctx.createBufferSource();
		source.channelCount=1;
		source.buffer=buffer;
		source.connect(This._dest);
		if(set.play){//播放出声音
			source.connect(ctx.destination);
		}
		source.onended=function(){
			source.disconnect();
			source.stop();
			
			This._createBuffer();//重新创建buffer
		};
		source.start();//古董 source.noteOn(0) 不支持onended 放弃支持
		
		This.bufferSource=source;
		This.audioBuffer=buffer;
		This.audioBufferIdx=0;
		This._createBufferTime=Date.now();
		
		This._writeBuffer();
	}
	,_writeBuffer:function(){
		var This=this,set=This.set;
		var buffer=This.audioBuffer;
		var sampleRate=This.bufferSampleRate;
		var oldAudioBufferIdx=This.audioBufferIdx;
		if(!buffer){
			return;
		}
		
		//计算已播放的量，可能已播放过头了，卡了没有数据
		var playSize=Math.floor((Date.now()-This._createBufferTime)/1000*sampleRate);
		if(This.audioBufferIdx+0.005*sampleRate<playSize){//5ms动态区间
			This.audioBufferIdx=playSize;//将写入位置修正到当前播放位置
		}
		//写进去了，但还未被播放的量
		var wnSize=Math.max(0, This.audioBufferIdx-playSize);
		
		//这次最大能写入多少；限制到800ms，包括写入了还未播放的
		var maxSize=buffer.length-This.audioBufferIdx;
		maxSize=Math.min(maxSize, ~~(0.8*sampleRate)-wnSize);
		if(maxSize<1){//写不下了，退出
			return;
		}
		
		if(This._subPause()){//暂停了，不消费缓冲数据
			return;
		};
		var pcms=This.pcmBuffer;
		var pcm0=pcms[0],pcm1=pcms[1],pcm1Len=pcm1.length;
		if(pcm0.length+pcm1Len==0){//无可用数据，退出
			This._playEnd();//无可播放数据回调
			return;
		};
		This._playLive();//有播放数据了
		
		var pcmSize=0,speed=1;
		var realMode=set.realtime;
		while(realMode){
			//************实时模式************
			//尽量同步播放，避免过大延迟，但始终保持延迟150ms播放新数据，这样每次添加进新数据都是接到还未播放到的最后面，减少引入的杂音，减少网络波动的影响
			var delaySecond=0.15;
			
			//计算当前堆积的量
			var dSize=wnSize+pcm0.length;
			var dMax=(realMode.maxDelay||300)/1000 *sampleRate;
			
			//堆积的在300ms内按正常播放
			if(dSize<dMax){
				//至少要延迟播放新数据
				var d150Size=Math.floor(delaySecond*sampleRate-dSize-pcm1Len);
				if(oldAudioBufferIdx==0 && d150Size>0){
					//开头加上少了的延迟
					This.audioBufferIdx=Math.max(This.audioBufferIdx, d150Size);
				}
				
				realMode=false;//切换成顺序播放
				break;
			}
			//堆积的太多，配置为全丢弃
			if(realMode.discardAll){
				if(dSize>dMax*1.333){//超过400ms，取200ms正常播放，300ms中位数
					pcm0=This._cutPcm0(Math.round(dMax*0.666-wnSize-pcm1Len));
				}
				realMode=false;//切换成顺序播放
				break;
			}
			
			//堆积的太多，要加速播放了，最多播放积压最后3秒的量，超过的直接丢弃
			pcm0=This._cutPcm0(3*sampleRate-wnSize-pcm1Len);
			
			speed=1.6;//倍速，重采样
			//计算要截取出来量
			pcmSize=Math.min(maxSize, Math.floor((pcm0.length+pcm1Len)/speed));
			break;
		}
		if(!realMode){
			//*******按顺序取数据播放*********
			//计算要截取出来量
			pcmSize=Math.min(maxSize, pcm0.length+pcm1Len);
		}
		if(!pcmSize){
			return;
		}
		
		//截取数据并写入到audioBuffer中
		This.audioBufferIdx=This._subWrite(buffer,pcmSize,This.audioBufferIdx,speed);
	}
	
	
	/****************兼容播放处理，播放音质略微差点****************/
	,_writeBad:function(){
		var This=this,set=This.set;
		var buffer=This.audioBuffer;
		var sampleRate=This.bufferSampleRate;
		var ctx=This._ctx;
		
		//正在播放，5ms不能结束就等待播放完，定时器是10ms
		if(buffer){
			var ms=buffer.length/sampleRate*1000;
			if(Date.now()-This._createBufferTime<ms-5){
				return;
			}
		}
		
		//这次最大能写入多少；限制到800ms
		var maxSize=~~(0.8*sampleRate);
		var st=set.PlayBufferDisable?0:sampleRate/1000*300;//缓冲播放，不然间隔太短接续爆音明显
		
		if(This._subPause()){//暂停了，不消费缓冲数据
			return;
		};
		var pcms=This.pcmBuffer;
		var pcm0=pcms[0],pcm1=pcms[1],pcm1Len=pcm1.length;
		var allSize=pcm0.length+pcm1Len;
		if(allSize==0 || allSize<st){//无可用数据 不够缓冲量，退出
			This._playEnd();//无可播放数据回调，最后一丁点会始终等缓冲满导致卡住
			return;
		};
		This._playLive();//有播放数据了
		
		var pcmSize=0,speed=1;
		var realMode=set.realtime;
		while(realMode){
			//************实时模式************
			//计算当前堆积的量
			var dSize=pcm0.length;
			var dMax=(realMode.maxDelay||300)/1000 *sampleRate;
			
			//堆积的在300ms内按正常播放
			if(dSize<dMax){
				realMode=false;//切换成顺序播放
				break;
			}
			//堆积的太多，配置为全丢弃
			if(realMode.discardAll){
				if(dSize>dMax*1.333){//超过400ms，取200ms正常播放，300ms中位数
					pcm0=This._cutPcm0(Math.round(dMax*0.666-pcm1Len));
				}
				realMode=false;//切换成顺序播放
				break;
			}
			
			//堆积的太多，要加速播放了，最多播放积压最后3秒的量，超过的直接丢弃
			pcm0=This._cutPcm0(3*sampleRate-pcm1Len);
			
			speed=1.6;//倍速，重采样
			//计算要截取出来量
			pcmSize=Math.min(maxSize, Math.floor((pcm0.length+pcm1Len)/speed));
			break;
		}
		if(!realMode){
			//*******按顺序取数据播放*********
			//计算要截取出来量
			pcmSize=Math.min(maxSize, pcm0.length+pcm1Len);
		}
		if(!pcmSize){
			return;
		}
		
		//新建buffer，一次性完整播放当前的数据
		buffer=ctx.createBuffer(1,pcmSize,sampleRate);
		
		//截取数据并写入到audioBuffer中
		This._subWrite(buffer,pcmSize,0,speed);
		
		//首尾进行1ms的淡入淡出 大幅减弱爆音
		FadeInOut(buffer.getChannelData(0), sampleRate);
		
		var source=ctx.createBufferSource();
		source.channelCount=1;
		source.buffer=buffer;
		source.connect(This._dest);
		if(set.play){//播放出声音
			source.connect(ctx.destination);
		}
		source.start();//古董 source.noteOn(0) 不支持onended 放弃支持
		
		This.bufferSource=source;
		This.audioBuffer=buffer;
		This._createBufferTime=Date.now();
	}
	
	
	
	
	
	,_cutPcm0:function(pcmNs){//保留堆积的数据到指定的时长数量
		var pcms=this.pcmBuffer,pcm0=pcms[0];
		if(pcmNs<0)pcmNs=0;
		if(pcm0.length>pcmNs){//丢弃超过秒数的
			var size=pcm0.length-pcmNs, dur=Math.round(size/this.bufferSampleRate*1000);
			pcm0=pcm0.subarray(size);
			pcms[0]=pcm0;
			CLog($T("L8sC::延迟过大，已丢弃{1}ms {2}",0,dur,size),3);
		}
		return pcm0;
	}
	,_subPause:function(){//暂停了，就不要消费掉缓冲数据了，等待resume再来消费
		var This=this;
		if(!This.isPause){
			return 0;
		};
		if(This.set.realtime){//实时模式，丢弃所有未消费的数据，resume时从最新input的数据开始播放
			This._subClear();
		};
		return 1;
	}
	,_subClear:function(){ //清除缓冲数据
		this.pcmBuffer=[[],[]];
	}
	,_subWrite:function(buffer, pcmSize, offset, speed){
		var This=this;
		var pcms=This.pcmBuffer;
		var pcm0=pcms[0],pcm1=pcms[1];
		
		//截取数据
		var pcm=new Int16Array(pcmSize);
		var i=0,n=0;
		for(var j=0;n<pcmSize && j<pcm0.length;){//简单重采样
			pcm[n++]=pcm0[i];
			j+=speed; i=Math.round(j);
		}
		if(i>=pcm0.length){//堆积的消耗完了
			pcm0=new Int16Array(0);
			
			for(j=0,i=0;n<pcmSize && j<pcm1.length;){
				pcm[n++]=pcm1[i];
				j+=speed; i=Math.round(j);
			}
			if(i>=pcm1.length){
				pcm1=new Int16Array(0);
			}else{
				pcm1=pcm1.subarray(i);
			}
			pcms[1]=pcm1;
		}else{
			pcm0=pcm0.subarray(i);
		}
		pcms[0]=pcm0;
		
		
		//写入到audioBuffer中
		var channel=buffer.getChannelData(0);
		for(var i=0;i<pcmSize;i++,offset++){
			channel[offset]=pcm[i]/0x7FFF;
		}
		
		This._Tc+=pcmSize;//更新已播放时长
		This._updateTime();
		
		return offset;
	}
	
};

var NoStartMsg=function(){
	return $T("TZPq::{1}未调用start方法",0,BufferStreamPlayerTxt);
};



/**pcm数据进行首尾1ms淡入淡出处理，播放时可以大幅减弱爆音**/
var FadeInOut=BufferStreamPlayer.FadeInOut=function(arr,sampleRate){
	var sd=sampleRate/1000*1;//浮点数，arr是Int16或者Float32
	for(var i=0;i<sd;i++){
		arr[i]*=i/sd;
	}
	for(var l=arr.length,i=~~(l-sd);i<l;i++){
		arr[i]*=(l-i)/sd;
	}
};

/**解码音频文件成pcm**/
var DecodeAudio=BufferStreamPlayer.DecodeAudio=function(arrayBuffer,True,False){
	var ctx=Recorder.GetContext();
	if(!ctx){//强制激活Recorder.Ctx 不支持大概率也不支持解码
		False&&False($T("iCFC::浏览器不支持音频解码"));
		return;
	};
	if(!arrayBuffer || !(arrayBuffer instanceof ArrayBuffer)){
		False&&False($T("wE2k::音频解码数据必须是ArrayBuffer"));
		return;//非ArrayBuffer 有日志但不抛异常 不会走回调
	};
	
	ctx.decodeAudioData(arrayBuffer,function(raw){
		var src=raw.getChannelData(0);
		var sampleRate=raw.sampleRate;
		
		var pcm=new Int16Array(src.length);
		for(var i=0;i<src.length;i++){//floatTo16BitPCM 
			var s=Math.max(-1,Math.min(1,src[i]));
			s=s<0?s*0x8000:s*0x7FFF;
			pcm[i]=s;
		};
		
		True&&True({
			sampleRate:sampleRate
			,duration:Math.round(src.length/sampleRate*1000)
			,data:pcm
		});
	},function(e){
		False&&False($T("mOaT::音频解码失败：{1}",0,e&&e.message||"-"));
	});
};

var CLog=function(){
	var v=arguments; v[0]="["+BufferStreamPlayerTxt+"]"+v[0];
	Recorder.CLog.apply(null,v);
};
Recorder[BufferStreamPlayerTxt]=BufferStreamPlayer;

	
}));