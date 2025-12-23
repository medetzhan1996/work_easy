import dragula from 'dragula';
import { ajaxPost } from './ajax';

/**
 * Handles drop event for Dragula instance.
 * @param {HTMLElement} el - The dragged element.
 * @param {HTMLElement} target - The target container.
 * @param {HTMLElement} source - The source container.
 * @param {HTMLElement} sibling - The sibling element.
 */
async function handleDrop(el, target, source, sibling) {
  const itemID = el.getAttribute('data-id');
  const parentBoardId = target.getAttribute('id');
  const sourceId = source.getAttribute('id');
  const url = `/sales_funnel/card-ajax/${itemID}/update`;
  const data = { 'funnel': parentBoardId };

  try {
    await ajaxPost(url, data);
  } catch (error) {
    console.error('Error updating card:', error);
  }
}

/**
 * Initialize Dragula with the given selector.
 * @param {string} selector - The CSS selector for the containers.
 */
const initializeDragula = (selector, callback) => {
  const containers = Array.from(document.querySelectorAll(selector));
  const drake = dragula(containers, {
    revertOnSpill: true,
  });
  callback(drake)
};

export {
  initializeDragula,
};