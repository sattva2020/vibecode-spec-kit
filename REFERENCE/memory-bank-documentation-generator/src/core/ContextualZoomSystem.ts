import { C4Element, C4Relationship } from "../types/C4Types";

export interface FocusArea {
    elementId: string;
    radius: number;
    context: string[];
}

export interface ZoomLevel {
    level: "overview" | "focused" | "detailed" | "expert";
    scale: number;
    focusElements: C4Element[];
    contextElements: C4Element[];
}

export interface ContextualInformation {
    focusedElement: C4Element;
    relatedElements: C4Element[];
    dependencies: C4Relationship[];
    metadata: any;
}

export class ContextualZoomSystem {
    private currentZoom: ZoomLevel = {
        level: "overview", 
        scale: 1, 
        focusElements: [], 
        contextElements: []
    };

    detectUserFocus(elements: C4Element[], mousePosition?: any): FocusArea {
        const focusedElement = mousePosition ? this.findElementAtPosition(elements, mousePosition) : null;
        return {
            elementId: focusedElement?.id || "",
            radius: 100,
            context: this.getContextElements(focusedElement, elements)
        };
    }

    calculateOptimalZoom(focus: FocusArea, diagram: any): ZoomLevel {
        if (!focus.elementId) {
            return {level: "overview", scale: 1, focusElements: [], contextElements: []};
        }
        const focusedElement = this.findElementById(focus.elementId, diagram.elements);
        const relatedElements = this.getRelatedElements(focusedElement, diagram);
        return {
            level: "focused",
            scale: 1.5,
            focusElements: [focusedElement],
            contextElements: relatedElements
        };
    }

    maintainContext(zoom: ZoomLevel): ContextualInformation {
        const focusedElement = zoom.focusElements[0];
        const relatedElements = zoom.contextElements;
        const dependencies = this.getDependencies(focusedElement, relatedElements);
        return {
            focusedElement: focusedElement,
            relatedElements: relatedElements,
            dependencies: dependencies,
            metadata: {zoomLevel: zoom.level, timestamp: new Date()}
        };
    }

    smoothTransition(from: ZoomLevel, to: ZoomLevel): any {
        const steps = this.calculateTransitionSteps(from, to);
        return {
            steps: steps,
            duration: 500,
            easing: "ease-in-out",
            onComplete: () => {
                this.currentZoom = to;
            }
        };
    }

    private findElementAtPosition(elements: C4Element[], position: any): C4Element | null {
        return elements.find(el => this.isElementAtPosition(el, position)) || null;
    }

    private isElementAtPosition(element: C4Element, position: any): boolean {
        if (!position || typeof position.x !== 'number' || typeof position.y !== 'number') {
            return false;
        }
        return Math.abs(position.x - (element.x || 0)) < 50 && Math.abs(position.y - (element.y || 0)) < 50;
    }

    private getContextElements(element: C4Element | null, allElements: C4Element[]): string[] {
        if (!element) return [];
        return allElements.filter(el => el.id !== element.id).map(el => el.id);
    }

    private findElementById(id: string, elements: C4Element[]): C4Element {
        return elements.find(el => el.id === id) || elements[0];
    }

    private getRelatedElements(element: C4Element, diagram: any): C4Element[] {
        const relationships = diagram.relationships || [];
        const relatedIds = relationships
            .filter((rel: any) => rel.from === element.id || rel.to === element.id)
            .map((rel: any) => rel.from === element.id ? rel.to : rel.from);
        return diagram.elements.filter((el: C4Element) => relatedIds.includes(el.id));
    }

    private getDependencies(focusedElement: C4Element, contextElements: C4Element[]): C4Relationship[] {
        return [];
    }

    private calculateTransitionSteps(from: ZoomLevel, to: ZoomLevel): any[] {
        const steps = [];
        const scaleDiff = to.scale - from.scale;
        const stepCount = 10;
        for (let i = 0; i <= stepCount; i++) {
            const progress = i / stepCount;
            steps.push({
                scale: from.scale + (scaleDiff * progress),
                focusElements: to.focusElements,
                contextElements: to.contextElements
            });
        }
        return steps;
    }
}