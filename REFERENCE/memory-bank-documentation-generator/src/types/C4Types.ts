import { ProjectInfo } from "./ProjectTypes";

export interface C4Diagram {
    id: string;
    type: "system-context" | "container" | "component" | "code";
    title: string;
    description: string;
    elements: C4Element[];
    relationships: C4Relationship[];
}

export interface C4Element {
    id: string;
    name: string;
    type: string;
    description: string;
    technology?: string;
    x?: number;
    y?: number;
}

export interface C4Relationship {
    from: string;
    to: string;
    label: string;
    technology?: string;
}

export interface C4Generator {
    generateSystemContext(project: ProjectInfo): C4Diagram;
    generateContainerDiagram(project: ProjectInfo): C4Diagram;
    generateComponentDiagram(project: ProjectInfo): C4Diagram;
    generateCodeDiagram(project: ProjectInfo): C4Diagram;
}