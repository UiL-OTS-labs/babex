declare global {
    interface Window {
        tinymce: any // eslint-disable-line @typescript-eslint/no-explicit-any

        getUser: () => User
    }
}

export default global;
