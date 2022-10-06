declare global {
    // eslint-disable-next-line
    let bootstrap: any
}

function makeToast(message: string, kind: string) {
    const toast = document.createElement('div');
    toast.classList.add('toast');
    toast.classList.add(`text-bg-${kind}`);
    toast.innerHTML = `<div class="toast-body">${message}</div>`;

    const container = document.getElementById('toast_container');
    if(container) {
        container.append(toast);
        (new bootstrap.Toast(toast)).show();
    }
    else {
        console.warn('Cannot show Toast, Missing toast_container');
    }
}

function error(message: string) {
    makeToast(message, 'error');
}

export { error };
