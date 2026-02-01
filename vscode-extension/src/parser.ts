import * as crypto from "crypto";

export type BlockType =
  | "definition"
  | "lemma"
  | "theorem"
  | "proposition"
  | "corollary"
  | "proof"
  | "remark"
  | "example";

export interface Block {
  type: BlockType;
  label: string | null;
  title: string | null;
  id: string;
  range: [number, number];
  latexFragment: string;
}

const BLOCK_TYPES: BlockType[] = [
  "definition",
  "lemma",
  "theorem",
  "proposition",
  "corollary",
  "proof",
  "remark",
  "example",
];

const PROVABLE_BLOCK_TYPES = new Set<BlockType>([
  "definition",
  "lemma",
  "theorem",
  "proposition",
  "corollary",
]);

const MAX_TITLE_LENGTH = 60;

function generateBlockId(
  blockType: string,
  start: number,
  content: string
): string {
  const hashInput = `${blockType}:${start}:${content.slice(0, 100)}`;
  const hash = crypto.createHash("md5").update(hashInput).digest("hex");
  return `blk_${hash.slice(0, 8)}`;
}

function extractLabel(content: string): string | null {
  const match = content.match(/\\label\{([^}]+)\}/);
  return match ? match[1] : null;
}

function extractTitle(
  optionalArg: string | undefined,
  content: string
): string | null {
  if (optionalArg) {
    return optionalArg.slice(1, -1).trim();
  }

  let cleaned = content.trim();
  cleaned = cleaned.replace(/\\label\{[^}]*\}/g, "").trim();
  if (!cleaned) {
    return null;
  }

  let firstLine = cleaned.split("\n")[0].trim();
  if (firstLine.length > MAX_TITLE_LENGTH) {
    firstLine = firstLine.slice(0, MAX_TITLE_LENGTH - 3) + "...";
  }
  return firstLine || null;
}

function getProofTitle(precedingBlocks: Block[]): string | null {
  for (let i = precedingBlocks.length - 1; i >= 0; i--) {
    const block = precedingBlocks[i];
    if (PROVABLE_BLOCK_TYPES.has(block.type)) {
      return block.title ? `${block.title} の証明` : null;
    }
  }
  return null;
}

export function extractBlocks(source: string): Block[] {
  const blocks: Block[] = [];
  const typesPattern = BLOCK_TYPES.join("|");
  const pattern = new RegExp(
    `\\\\begin\\{(${typesPattern})\\}(\\[[^\\]]*\\])?([\\s\\S]*?)\\\\end\\{\\1\\}`,
    "g"
  );

  let match: RegExpExecArray | null;
  while ((match = pattern.exec(source)) !== null) {
    const blockType = match[1] as BlockType;
    const optionalArg = match[2];
    const content = match[3];
    const start = match.index;
    const end = start + match[0].length;

    const label = extractLabel(content);
    const blockId = label ?? generateBlockId(blockType, start, content);
    let title = extractTitle(optionalArg, content);

    if (blockType === "proof" && !optionalArg) {
      title = getProofTitle(blocks);
    }

    blocks.push({
      type: blockType,
      label,
      title,
      id: blockId,
      range: [start, end],
      latexFragment: match[0],
    });
  }

  return blocks;
}
