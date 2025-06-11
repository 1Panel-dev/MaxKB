type menusItemType = {
  label: string;
  style?: {
    [key: string]: string | number
  }
  icon?: string | unknown;
  disabled?: boolean;
  divided?: boolean;
  enter?: (menu: menusItemType, args: unknown) => unknown;
  click?: (menu: menusItemType, args: unknown) => unknown;
  children?: Array<menusItemType>;
  tip?: string;
  hidden?: boolean;
}

type menusType = {
  menus: Array<menusItemType>;
  menusClass?: string;
  itemClass?: string;
  minWidth?: number | string;
  maxWidth?: number | string;
  zIndex?: number | string;
  direction?: "left" | "right";
}

type componentMenusType = menusType & {
  event: MouseEvent;
  open: boolean;
  args?: unknown
}

declare module 'vue3-menus' {
  export const Vue3Menus: import('vue').DefineComponent<componentMenusType, componentMenusType, componentMenusType, componentMenusType, componentMenusType,
    componentMenusType, componentMenusType, componentMenusType, componentMenusType, componentMenusType, componentMenusType, componentMenusType>;

  export const menusEvent: (event: MouseEvent, menus: menusType | Array<menusItemType>, args: unknown) => void;

  export const directive: import('vue').Directive<any, menusType | Array<menusItemType>>;

  const install: (app: import('vue').App, options: {
    name: string
  }) => unknown;
  export default install;
}

export {
  menusType,
  menusItemType
}
