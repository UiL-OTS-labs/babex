declare global {
    let bootstrap: any
}

function makeToast(message: string, kind: string) {
    const toast = document.createElement('div');
    toast.classList.add('toast');
    toast.classList.add(`text-bg-${kind}`);
    toast.innerHTML = `<div class="toast-body">${message}</div>`;

    document.getElementById('toast_container')!.append(toast);
    (new bootstrap.Toast(toast)).show();
}

function error(message: string) {
    makeToast(message, 'error');
}

export { error };
