export type LocaleShape<T> = {
  readonly [Key in keyof T]: T[Key] extends string
    ? string
    : LocaleShape<T[Key]>;
};
