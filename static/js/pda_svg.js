// Custom SVG Layout Engine for PDA (ported from pda_panel.py)

const SCALE_X = 1.5;
const SCALE_Y = 1.4;
const OFFSET_X = 150;

function sx(x) { return (x - 250) * SCALE_X + 250 + OFFSET_X; }
function sy(y) { return y * SCALE_Y; }

function createSVG(width, height) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('width', width);
  svg.setAttribute('height', height);
  svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
  
  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
  // Arrowhead marker
  const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
  marker.setAttribute('id', 'arrowhead');
  marker.setAttribute('markerWidth', '10');
  marker.setAttribute('markerHeight', '7');
  marker.setAttribute('refX', '9');
  marker.setAttribute('refY', '3.5');
  marker.setAttribute('orient', 'auto');
  
  const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
  polygon.setAttribute('points', '0 0, 10 3.5, 0 7');
  polygon.setAttribute('fill', '#6c7086');
  marker.appendChild(polygon);
  
  defs.appendChild(marker);
  svg.appendChild(defs);
  
  const gEdges = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  gEdges.setAttribute('id', 'edges');
  svg.appendChild(gEdges);
  
  const gNodes = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  gNodes.setAttribute('id', 'nodes');
  svg.appendChild(gNodes);
  
  svg.gEdges = gEdges;
  svg.gNodes = gNodes;
  
  return svg;
}

function drawNode(svg, type, x, y, id, labelText) {
  x = sx(x); y = sy(y);
  
  const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  g.setAttribute('class', 'node');
  g.setAttribute('id', id);
  g.style.cursor = 'pointer';
  
  let bg;
  const stroke = type === 'decision' ? '#89b4fa' : (type === 'start' ? '#a6e3a1' : (type === 'accept' ? '#a6e3a1' : '#f38ba8'));
  const fill = '#313244';
  
  if (type === 'decision') {
    bg = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    bg.setAttribute('points', `${x},${y-30} ${x+30},${y} ${x},${y+30} ${x-30},${y}`);
  } else {
    bg = document.createElementNS('http://www.w3.org/2000/svg', 'ellipse');
    bg.setAttribute('cx', x);
    bg.setAttribute('cy', y);
    bg.setAttribute('rx', 35);
    bg.setAttribute('ry', 20);
  }
  
  bg.setAttribute('fill', fill);
  bg.setAttribute('stroke', stroke);
  bg.setAttribute('stroke-width', '2');
  g.appendChild(bg);
  
  const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  text.setAttribute('x', x);
  text.setAttribute('y', y + 4);
  text.setAttribute('text-anchor', 'middle');
  text.setAttribute('fill', '#cdd6f4');
  text.setAttribute('font-family', 'Segoe UI, Helvetica, sans-serif');
  text.setAttribute('font-size', '11px');
  if (type === 'decision') text.setAttribute('font-weight', 'bold');
  text.textContent = labelText;
  g.appendChild(text);
  
  svg.gNodes.appendChild(g);
}

function drawPath(svg, points, textStr, textPos) {
  const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  g.setAttribute('class', 'edge');
  
  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  let d = `M ${points[0].x} ${points[0].y}`;
  for (let i = 1; i < points.length; i++) {
    d += ` L ${points[i].x} ${points[i].y}`;
  }
  path.setAttribute('d', d);
  path.setAttribute('fill', 'none');
  path.setAttribute('stroke', '#6c7086');
  path.setAttribute('stroke-width', '2');
  path.setAttribute('marker-end', 'url(#arrowhead)');
  g.appendChild(path);
  
  if (textStr) {
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', textPos.x);
    text.setAttribute('y', textPos.y);
    text.setAttribute('fill', '#a6adc8');
    text.setAttribute('font-family', 'Segoe UI, Helvetica, sans-serif');
    text.setAttribute('font-size', '12px');
    text.setAttribute('font-weight', 'bold');
    
    // add small background for text
    const filter = document.createElementNS('http://www.w3.org/2000/svg', 'filter');
    filter.setAttribute('id', 'solid');
    filter.setAttribute('x', '0'); filter.setAttribute('y', '0'); filter.setAttribute('width', '1'); filter.setAttribute('height', '1');
    filter.innerHTML = `<feFlood flood-color="#1e1e2e"/><feComposite in="SourceGraphic"/>`;
    text.setAttribute('filter', 'url(#solid)');
    
    text.textContent = textStr;
    g.appendChild(text);
  }
  
  svg.gEdges.appendChild(g);
}

function drawOrthoArrow(svg, x1, y1, x2, y2, label, bend, bendPos) {
  const ox1 = x1, oy1 = y1, ox2 = x2, oy2 = y2;
  x1 = sx(x1); y1 = sy(y1);
  x2 = sx(x2); y2 = sy(y2);
  
  let points = [{x: x1, y: y1}];
  
  if (bend === 'v') {
    if (bendPos !== undefined) {
      points.push({x: x1, y: sy(bendPos)});
      points.push({x: x2, y: sy(bendPos)});
      points.push({x: x2, y: y2});
    } else {
      points.push({x: x1, y: y2});
      points.push({x: x2, y: y2});
    }
  } else if (bend === 'h') {
    if (bendPos !== undefined) {
      points.push({x: sx(bendPos), y: y1});
      points.push({x: sx(bendPos), y: y2});
      points.push({x: x2, y: y2});
    } else {
      points.push({x: x2, y: y1});
      points.push({x: x2, y: y2});
    }
  } else if (bend === 'hv') {
    let midX = bendPos !== undefined ? sx(bendPos) : x2;
    points.push({x: midX, y: y1});
    points.push({x: midX, y: y2});
    points.push({x: x2, y: y2});
  } else if (bend === 'vh') {
    let midY = bendPos !== undefined ? sy(bendPos) : y2;
    points.push({x: x1, y: midY});
    points.push({x: x2, y: midY});
    points.push({x: x2, y: y2});
  }

  // Deduplicate points so we don't have zero-length segments that confuse marker orientation
  const deduped = [points[0]];
  for (let i = 1; i < points.length; i++) {
    const prev = deduped[deduped.length - 1];
    if (Math.abs(points[i].x - prev.x) > 0.1 || Math.abs(points[i].y - prev.y) > 0.1) {
      deduped.push(points[i]);
    }
  }
  points = deduped;
  
  // Calculate text position roughly midway
  const textPos = {
    x: (x1 + x2) / 2 + 5,
    y: (y1 + y2) / 2 - 5
  };
  
  if (bend === 'v') {
    if (ox1 === ox2) { textPos.x = x1 + 5; textPos.y = (y1 + y2) / 2; }
    else { textPos.x = x1 + 5; textPos.y = y2 - 5; }
  } else if (bend === 'h') {
    if (oy1 === oy2) { textPos.x = (x1 + x2) / 2; textPos.y = y1 - 5; }
    else { textPos.x = x2 + 5; textPos.y = y1 - 5; }
  }
  
  drawPath(svg, points, label, textPos);
}

function drawLoop(svg, cx, cy, label, dir = 'right') {
  cx = sx(cx); cy = sy(cy);
  
  const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  g.setAttribute('class', 'edge');
  
  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  let d;
  let textPos;
  
  if (dir === 'right') {
    d = `M ${cx + 15} ${cy - 15} C ${cx + 70} ${cy - 50}, ${cx + 70} ${cy + 50}, ${cx + 15} ${cy + 15}`;
    textPos = { x: cx + 55, y: cy + 5 };
  } else if (dir === 'left') {
    d = `M ${cx - 15} ${cy - 15} C ${cx - 70} ${cy - 50}, ${cx - 70} ${cy + 50}, ${cx - 15} ${cy + 15}`;
    textPos = { x: cx - 75, y: cy + 5 };
  } else if (dir === 'bottom') {
    d = `M ${cx - 15} ${cy + 15} C ${cx - 50} ${cy + 70}, ${cx + 50} ${cy + 70}, ${cx + 15} ${cy + 15}`;
    textPos = { x: cx - 10, y: cy + 75 };
  }
  
  path.setAttribute('d', d);
  path.setAttribute('fill', 'none');
  path.setAttribute('stroke', '#6c7086');
  path.setAttribute('stroke-width', '2');
  path.setAttribute('marker-end', 'url(#arrowhead)');
  g.appendChild(path);
  
  const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  text.setAttribute('x', textPos.x);
  text.setAttribute('y', textPos.y);
  text.setAttribute('fill', '#a6adc8');
  text.setAttribute('font-family', 'Segoe UI, Helvetica, sans-serif');
  text.setAttribute('font-size', '12px');
  text.setAttribute('font-weight', 'bold');
  text.textContent = label;
  g.appendChild(text);
  
  svg.gEdges.appendChild(g);
}

function renderExpr1Svg() {
  const svg = createSVG(800, 1200);
  
  const cx = 250;
  const y_spacing = 80;
  let y = 30;
  
  drawNode(svg, 'start', cx, y, 'Start', 'Start');
  
  y += y_spacing;
  drawNode(svg, 'decision', cx, y, 'Read1', 'Read');
  drawOrthoArrow(svg, cx, y - y_spacing + 20, cx, y - 25, '', 'v');
  
  const y_branch_top = y + 120;
  const y_reject = y + 220;
  const y_branch_bottom = y + 320;
  
  drawNode(svg, 'reject', cx, y_reject, 'Reject', 'Reject');
  drawOrthoArrow(svg, cx, y + 25, cx, y_reject - 35, 'null', 'v');
  
  const left_x = cx - 140;
  const right_x = cx + 140;
  
  drawNode(svg, 'decision', left_x, y_branch_top, 'ReadB1', 'Read');
  drawOrthoArrow(svg, cx - 25, y, left_x, y_branch_top - 25, 'b', 'hv');
  
  drawNode(svg, 'decision', right_x, y_branch_top, 'ReadA1', 'Read');
  drawOrthoArrow(svg, cx + 25, y, right_x, y_branch_top - 25, 'a', 'hv');
  
  drawOrthoArrow(svg, left_x + 15, y_branch_top + 15, cx - 20, y_reject - 20, 'b', 'v', y_branch_top + 45);
  drawOrthoArrow(svg, right_x - 15, y_branch_top + 15, cx + 20, y_reject - 20, 'a', 'v', y_branch_top + 45);
  
  drawNode(svg, 'decision', left_x, y_branch_bottom, 'ReadB2', 'Read');
  drawOrthoArrow(svg, left_x, y_branch_top + 25, left_x, y_branch_bottom - 25, 'a', 'v');
  
  drawNode(svg, 'decision', right_x, y_branch_bottom, 'ReadA2', 'Read');
  drawOrthoArrow(svg, right_x, y_branch_top + 25, right_x, y_branch_bottom - 25, 'b', 'v');
  
  drawOrthoArrow(svg, left_x + 25, y_branch_bottom, cx - 25, y_reject + 15, 'a', 'h', left_x + 60);
  drawOrthoArrow(svg, right_x - 25, y_branch_bottom, cx + 25, y_reject + 15, 'b', 'h', right_x - 60);
  
  y = y_branch_bottom + y_spacing;
  drawNode(svg, 'decision', cx, y, 'ReadLoop', 'Read');
  drawOrthoArrow(svg, left_x + 15, y_branch_bottom + 15, cx - 15, y - 15, 'b', 'v', y_branch_bottom + 40);
  drawOrthoArrow(svg, right_x - 15, y_branch_bottom + 15, cx + 15, y - 15, 'a', 'v', y_branch_bottom + 40);
  drawLoop(svg, cx, y, 'a');
  
  y += y_spacing;
  drawNode(svg, 'decision', cx, y, 'ReadBab1', 'Read');
  drawOrthoArrow(svg, cx, y - y_spacing + 25, cx, y - 25, 'b', 'v');
  drawOrthoArrow(svg, cx + 25, y, cx + 15, y - y_spacing + 15, 'b', 'h', cx + 60); // Restart search
  
  y += y_spacing;
  drawNode(svg, 'decision', cx, y, 'ReadBab2', 'Read');
  drawOrthoArrow(svg, cx, y - y_spacing + 25, cx, y - 25, 'a', 'v');
  drawOrthoArrow(svg, cx + 25, y, cx + 20, y - y_spacing * 2 + 15, 'a', 'h', cx + 100); // Back to top
  
  y += y_spacing;
  drawNode(svg, 'decision', cx, y, 'ReadBab3', 'Read');
  drawOrthoArrow(svg, cx, y - y_spacing + 25, cx, y - 25, 'b', 'v');
  drawLoop(svg, cx, y, 'a,b');
  
  y += y_spacing;
  drawNode(svg, 'accept', cx, y, 'Accept', 'Accept');
  drawOrthoArrow(svg, cx, y - y_spacing + 25, cx, y - 20, 'null', 'v');
  
  return svg;
}

function renderExpr2Svg() {
  const svg = createSVG(800, 1200);
  
  const cx = 250;
  const y_top = 120;
  const y_reject = 200;
  const y_row1 = 240;
  const y_row2 = 340;
  const y_row3 = 400;
  const y_row4 = 600;
  const y_row5 = 700;
  const y_accept = 800;
  
  const col_L2 = cx - 200;
  const col_L1 = cx - 100;
  const col_C = cx;
  const col_R1 = cx + 100;
  const col_R2 = cx + 200;
  
  drawNode(svg, 'start', col_C, 30, 'Start', 'Start');
  drawNode(svg, 'decision', col_C, y_top, 'D_Top', 'Read');
  drawNode(svg, 'reject', col_C, y_reject, 'Reject', 'Reject');
  drawNode(svg, 'decision', col_L2, y_row1, 'D_L1', 'Read');
  drawNode(svg, 'decision', col_R2, y_row1, 'D_R1', 'Read');
  drawNode(svg, 'decision', col_L2, y_row2, 'D_L2', 'Read');
  drawNode(svg, 'decision', col_R1, y_row2, 'D_M_Right', 'Read');
  drawNode(svg, 'decision', col_R2, y_row2, 'D_R2', 'Read');
  drawNode(svg, 'decision', col_L1, y_row3, 'D_M_Left', 'Read');
  drawNode(svg, 'decision', col_L2, y_row4, 'D_L3', 'Read');
  drawNode(svg, 'decision', col_C, y_row4, 'D_q7', 'Read');
  drawNode(svg, 'decision', col_R2, y_row4, 'D_R3', 'Read');
  drawNode(svg, 'decision', col_R1, y_row5, 'D_BR', 'Read');
  drawNode(svg, 'accept', col_C, y_accept, 'Accept', 'Accept');
  
  drawOrthoArrow(svg, col_C, 55, col_C, y_top - 25, '', 'v');
  drawOrthoArrow(svg, col_C, y_top + 25, col_C, y_reject - 25, 'null', 'v');
  drawOrthoArrow(svg, col_C - 25, y_top, col_L2, y_row1 - 25, '1', 'hv');
  drawOrthoArrow(svg, col_C + 25, y_top, col_R2, y_row1 - 25, '0', 'hv');
  
  drawOrthoArrow(svg, col_L2, y_row1 + 25, col_L2, y_row2 - 25, '1', 'v');
  drawOrthoArrow(svg, col_L2 + 15, y_row1 + 15, col_R2 - 10, y_row2 - 20, '0', 'v', y_row1 + 45);
  
  drawOrthoArrow(svg, col_R2, y_row1 + 25, col_R2, y_row2 - 25, '0', 'v');
  drawOrthoArrow(svg, col_R2 - 15, y_row1 + 15, col_R1, y_row2 - 25, '1', 'v', y_row1 + 60);
  
  drawOrthoArrow(svg, col_L2, y_row2 + 25, col_L2, y_row4 - 25, '1', 'v');
  drawOrthoArrow(svg, col_L2 + 15, y_row2 + 15, col_L1, y_row3 - 25, '0', 'v', y_row3 - 40);
  
  drawOrthoArrow(svg, col_R1, y_row2 + 25, col_R1, y_row5 - 25, '1', 'v');
  drawOrthoArrow(svg, col_R1 - 15, y_row2 + 15, col_L1 + 10, y_row3 - 20, '0', 'v', y_row3 - 40);
  
  drawOrthoArrow(svg, col_R2, y_row2 + 25, col_R2, y_row4 - 25, '1', 'v');
  drawOrthoArrow(svg, col_R2 - 15, y_row2 + 15, col_C + 15, y_row4 - 15, '0', 'v', 500);
  
  drawOrthoArrow(svg, col_L1 + 15, y_row3 + 15, col_C - 15, y_row4 - 15, '0', 'v', y_row3 + 45);
  drawOrthoArrow(svg, col_L1, y_row3 + 25, col_C - 20, y_accept - 25, '1', 'v', 750);
  
  drawOrthoArrow(svg, col_L2, y_row4 + 25, col_C - 30, y_accept - 20, '1', 'v', 730);
  drawOrthoArrow(svg, col_L2 + 25, y_row4, col_L1 - 15, y_row3 + 15, '0', 'v', 470);
  
  drawOrthoArrow(svg, col_C, y_row4 + 25, col_C, y_accept - 25, '0', 'v');
  drawOrthoArrow(svg, col_C + 25, y_row4, col_R2 - 25, y_row4, '1', 'vh');
  
  drawOrthoArrow(svg, col_R2 - 15, y_row4 + 15, col_R1 + 15, y_row5 - 15, '1', 'v', y_row4 + 50);
  drawOrthoArrow(svg, col_R2 - 25, y_row4, col_L1 + 15, y_row3 + 15, '0', 'v', 470);
  
  drawOrthoArrow(svg, col_R1, y_row5 + 25, col_C + 20, y_accept - 25, '1', 'v', 750);
  
  const pts = [
    {x: sx(col_R1 - 25), y: sy(y_row5)},
    {x: sx(col_C + 50), y: sy(y_row5)},
    {x: sx(col_C + 50), y: sy(485)},
    {x: sx(col_L1 + 5), y: sy(485)},
    {x: sx(col_L1 + 5), y: sy(y_row3 + 20)}
  ];
  drawPath(svg, pts, '0', {x: sx(col_C + 55), y: sy(470)});
  
  drawLoop(svg, col_C, y_accept, '0, 1', 'bottom');
  
  return svg;
}

window.renderPDASvg = function(isExpr2) {
  if (isExpr2) return renderExpr2Svg();
  return renderExpr1Svg();
};
