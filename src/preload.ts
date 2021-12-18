import { ipcRenderer, ContextBridge, contextBridge } from "electron";
import { cpus } from "os";

contextBridge.exposeInMainWorld("api", {
	threads: cpus().length,
});
