class Region {

    private type: string;
    private documentID: any;
    private pageNr: number;
    private number: number;
    private text: string;
    private x: number;
    private y: number;
    private width: number;
    private height: number;
    private label: number;
    private labelColor: string;
    private mergedFrom: number[];

    constructor(type: string, object: any, labelColor: string) {
        this.type = type;
        this.text = object[type + "_text"];
        this.documentID = object.document_id;
        this.pageNr = object.page_nr;
        this.number = object[type + "_nr"];
        this.x = object.x;
        this.y = object.y;
        this.width = object.width;
        this.height = object.height;
        this.label = object.label;
        this.labelColor = labelColor;
        this.mergedFrom = object.merged;
    }

    public getType(): string {
        return this.type
    }

    public getDocumentID(): any {
        return this.documentID;
    }

    public getPageNR(): number {
        return this.pageNr;
    }

    public getNumber(): number {
        return this.number;
    }

    public getText(): string {
        return this.text;
    }

    public getX(): number {
        return this.x;
    }

    public getY(): number {
        return this.y;
    }

    public getWidth(): number {
        return this.width;
    }

    public getHeight(): number {
        return this.height;
    }

    public getLabel(): number {
        return this.label;
    }

    public getLabelColor(): string {
        return this.labelColor;
    }

    public getMergedFrom(): number[] {
        return this.mergedFrom;
    }

}

export default Region