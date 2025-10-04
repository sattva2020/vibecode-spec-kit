import { C4Diagram, C4Element, C4Relationship } from "../types/C4Types";

export class MermaidRenderer {
    renderC4Diagram(diagram: C4Diagram): string {
        const mermaidCode = this.generateMermaidCode(diagram);
        return mermaidCode;
    }

    generateMermaidCode(diagram: C4Diagram): string {
        let mermaidCode = "graph TB\n";
        mermaidCode += this.generateElementDefinitions(diagram.elements);
        mermaidCode += this.generateRelationshipDefinitions(diagram.relationships);
        return mermaidCode;
    }

    private generateElementDefinitions(elements: C4Element[]): string {
        let definitions = "";
        for (const element of elements) {
            const elementId = this.sanitizeId(element.id);
            const elementLabel = this.escapeLabel(element.name);
            definitions += elementId + "[" + elementLabel + " - " + element.description + "]\n";
        }
        return definitions;
    }

    private generateRelationshipDefinitions(relationships: C4Relationship[]): string {
        let definitions = "";
        for (const relationship of relationships) {
            const fromId = this.sanitizeId(relationship.from);
            const toId = this.sanitizeId(relationship.to);
            const label = this.escapeLabel(relationship.label);
            definitions += fromId + " -->|" + label + "| " + toId + "\n";
        }
        return definitions;
    }

    private sanitizeId(id: string): string {
        return id.replace(/[^a-zA-Z0-9_]/g, "_");
    }

    private escapeLabel(label: string): string {
        return label.replace(/"/g, "\\\"").replace(/\n/g, " ");
    }

    renderSystemContext(diagram: C4Diagram): string {
        let mermaidCode = "graph TB\n";
        mermaidCode += "subgraph External_Users\n";
        mermaidCode += "DEV[Developer]\n";
        mermaidCode += "AI[AI Assistant]\n";
        mermaidCode += "TEAM[Development Team]\n";
        mermaidCode += "end\n\n";
        
        mermaidCode += "subgraph Memory_Bank_System\n";
        mermaidCode += "MB[Memory Bank Core]\n";
        mermaidCode += "end\n\n";
        
        mermaidCode += "subgraph External_Systems\n";
        mermaidCode += "CURSOR[Cursor IDE]\n";
        mermaidCode += "GIT[Git Repository]\n";
        mermaidCode += "DOCKER[Docker Environment]\n";
        mermaidCode += "end\n\n";
        
        mermaidCode += "DEV --> MB\n";
        mermaidCode += "AI --> MB\n";
        mermaidCode += "TEAM --> MB\n";
        mermaidCode += "MB --> CURSOR\n";
        mermaidCode += "MB --> GIT\n";
        mermaidCode += "MB --> DOCKER\n";
        
        return mermaidCode;
    }

    renderContainerDiagram(diagram: C4Diagram): string {
        let mermaidCode = "graph TB\n";
        mermaidCode += "subgraph Memory_Bank_System\n";
        mermaidCode += "MB[Memory Bank Core]\n";
        mermaidCode += "AF[Advanced Features]\n";
        mermaidCode += "RS[Rust Microservices]\n";
        mermaidCode += "DG[Documentation Generator]\n";
        mermaidCode += "end\n\n";
        
        mermaidCode += "subgraph Data_Storage\n";
        mermaidCode += "FS[File System]\n";
        mermaidCode += "DB[Database]\n";
        mermaidCode += "CACHE[Cache]\n";
        mermaidCode += "end\n\n";
        
        mermaidCode += "subgraph External_Services\n";
        mermaidCode += "API[External APIs]\n";
        mermaidCode += "MONITOR[Monitoring]\n";
        mermaidCode += "end\n\n";
        
        mermaidCode += "MB --> AF\n";
        mermaidCode += "MB --> RS\n";
        mermaidCode += "MB --> DG\n";
        mermaidCode += "MB --> FS\n";
        mermaidCode += "MB --> DB\n";
        mermaidCode += "RS --> CACHE\n";
        mermaidCode += "RS --> API\n";
        mermaidCode += "RS --> MONITOR\n";
        
        return mermaidCode;
    }

    renderComponentDiagram(diagram: C4Diagram): string {
        let mermaidCode = "graph TB\n";
        mermaidCode += "subgraph Memory_Bank_Core\n";
        mermaidCode += "VAN[VAN Mode]\n";
        mermaidCode += "PLAN[PLAN Mode]\n";
        mermaidCode += "CREATIVE[CREATIVE Mode]\n";
        mermaidCode += "IMPLEMENT[IMPLEMENT Mode]\n";
        mermaidCode += "REFLECT[REFLECT Mode]\n";
        mermaidCode += "ARCHIVE[ARCHIVE Mode]\n";
        mermaidCode += "end\n\n";
        
        mermaidCode += "VAN --> PLAN\n";
        mermaidCode += "PLAN --> CREATIVE\n";
        mermaidCode += "CREATIVE --> IMPLEMENT\n";
        mermaidCode += "IMPLEMENT --> REFLECT\n";
        mermaidCode += "REFLECT --> ARCHIVE\n";
        
        return mermaidCode;
    }
}