import mitt from "mitt";
const bus: any = {};
const emitter = mitt();
bus.on = emitter.on;
bus.off = emitter.off;
bus.emit = emitter.emit;

export default bus;
