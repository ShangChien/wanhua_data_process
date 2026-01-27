import { PluginContext } from "molstar/lib/mol-plugin/context";
import { DefaultPluginSpec } from "molstar/lib/mol-plugin/spec";

export async function createRootViewer() {
  const viewport = document.getElementById("app") as HTMLDivElement;
  const canvas = document.getElementById("canvas") as HTMLCanvasElement;

  const plugin = new PluginContext(DefaultPluginSpec());
  await plugin.init();

  if (!plugin.initViewer(canvas, viewport)) {
    viewport.innerHTML = "Failed to init Mol*";
    throw new Error("init failed");
  }
  //@ts-ignore
  window["molstar"] = plugin;

  return plugin;
}

export async function init() {
  // Create viewer
  const plugin = await createRootViewer();

  // Download PDB
  const fileData = await plugin.builders.data.download({
    url: "https://models.rcsb.org/4hhb.bcif",
    isBinary: true,
  });

  // Load PDB and create representation
  const trajectory = await plugin.builders.structure.parseTrajectory(
    fileData,
    "mmcif"
  );
  await plugin.builders.structure.hierarchy.applyPreset(trajectory, "default");
}
