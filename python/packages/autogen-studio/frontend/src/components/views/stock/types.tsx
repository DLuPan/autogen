export interface DataPanel {
  id: string;
  title: string;
  type: "stock";
}

export const defaultDataPanels: DataPanel[] = [
  {
    id: "stock-info",
    title: "Stock info",
    type: "stock",
  }
];
