import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="추억의 오락실 비행기", page_icon="🕹️", layout="centered")

st.title("🕹️ 추억의 오락실 비행기: 랭킹전")
st.markdown("무적 버그 해결! 이제 스치면 사망합니다. \n* ⚡**레이저:** 에너지가 100% 모이면 자동 발사! \n* 💣**필살기:** 화면 빈 곳을 **더블 터치(따닥!)**")
st.markdown("---")

game_html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  body { display: flex; flex-direction: column; align-items: center; background-color: #0d1117; color: white; margin: 0; padding: 10px; touch-action: none; font-family: 'Arial', sans-serif;}
  canvas { border-radius: 12px; box-shadow: 0 0 25px rgba(0, 255, 255, 0.2); border: 2px solid #30363d; cursor: crosshair;}
  
  .status-bar { width: 350px; display: flex; justify-content: space-between; font-weight: bold; font-size: 16px; margin-bottom: 8px; }
  .energy-container { width: 350px; height: 16px; background: #21262d; border-radius: 8px; margin-bottom: 12px; border: 1px solid #484f58; position: relative; overflow: hidden; }
  #energy-bar { height: 100%; width: 0%; background: linear-gradient(90deg, #00f2fe, #f5576c); transition: width 0.1s; }
  #energy-text { position: absolute; top: -1px; left: 38%; font-size: 13px; font-weight: bold; text-shadow: 1px 1px 2px black;}
  .info-bar { width: 350px; display: flex; justify-content: space-between; font-size: 14px; font-weight: bold; margin-bottom: 5px; color: #58a6ff;}

  #game-over-screen { position: absolute; top: 150px; text-align: center; display: none; width: 350px; background: rgba(0,0,0,0.9); padding: 20px; border-radius: 15px; box-sizing: border-box; border: 2px solid #ff7b72; box-shadow: 0 0 20px rgba(255,0,0,0.5);}
  #game-over-text { color: #ff7b72; font-size: 36px; font-weight: 900; text-shadow: 0 0 15px red; margin-bottom: 15px;}
  
  #new-record-input { display: none; margin-bottom: 15px; }
  #new-record-input input { width: 90px; font-size: 26px; text-align: center; text-transform: uppercase; font-weight: bold; margin: 10px; border-radius: 5px; border: 2px solid #FFD700; background: #222; color: white;}
  #new-record-input button { padding: 8px 15px; font-size: 18px; font-weight: bold; background: #FFD700; color: black; border: none; border-radius: 5px; cursor: pointer;}
  
  #leaderboard { display: none; margin-bottom: 20px; text-align: left; }
  #leaderboard h3 { margin: 0 0 10px 0; text-align: center; color: #00FFFF; }
  .rank-row { display: flex; justify-content: space-between; font-size: 18px; margin-bottom: 5px; border-bottom: 1px solid #444; padding-bottom: 3px;}
  
  #btn-restart { padding: 12px 24px; font-size: 18px; font-weight: bold; background: #e34c26; color: white; border: none; border-radius: 8px; cursor: pointer; width: 100%;}
</style>
</head>
<body>
  
  <div class="status-bar">
      <span id="score" style="color: #f2cc60;">🏆 점수: 0</span>
      <span id="weapon" style="color: #79c0ff;">⚡무기: Lv.1</span>
  </div>
  
  <div class="info-bar">
      <span id="stage-name">📍 지역: 우주 궤도</span>
      <span id="bomb-ui">💣 폭탄: 2개 (따닥!)</span>
  </div>

  <div class="energy-container">
      <div id="energy-bar"></div>
      <span id="energy-text">0% (자동발사)</span>
  </div>

  <canvas id="gameCanvas" width="350" height="500"></canvas>

  <div id="game-over-screen">
      <div id="game-over-text">GAME OVER</div>
      
      <div id="new-record-input">
          <p style="color:#FFD700; margin:0; font-size:22px; font-weight:bold;">🎉 랭킹 달성! 🎉</p>
          <p style="color:white; margin:5px 0 0 0; font-size:14px;">이니셜 3자리를 새겨주세요</p>
          <input type="text" id="initials" maxlength="3" placeholder="AAA">
          <button onclick="saveScore()">등록</button>
      </div>
      
      <div id="leaderboard">
          <h3>🏆 명예의 전당 🏆</h3>
          <div id="leaderboard-list"></div>
      </div>
      
      <button id="btn-restart" onclick="resetGame()">🚀 다시 출격하기</button>
  </div>

<script>
  const canvas = document.getElementById("gameCanvas");
  const ctx = canvas.getContext("2d");

  let score = 0; let level = 1; let energy = 0; let bombs = 2; let weaponLevel = 1; let gameOver = false; let frameCount = 0;
  let isLaserActive = false; let laserTimer = 0;

  const player = { x: 175, y: 400, radius: 15, emoji: "✈️", invincible: 0 };
  let bullets = []; let enemyBullets = []; let enemies = []; let items = []; let particles = []; let shockwaves = [];
  let backgroundStars = [];

  const stages = [
      { min: 0,   name: "우주 궤도", c1: "#000015", c2: "#1a0b2e", e: ["👾", "👽", "☄️"], b: "🛸" },
      { min: 50,  name: "푸른 바다", c1: "#001f3f", c2: "#0074D9", e: ["🦑", "🐙", "🐡"], b: "🦈" },
      { min: 100, name: "붉은 사막", c1: "#4a1c00", c2: "#b05e00", e: ["🦂", "🐍", "🦇"], b: "🦅" },
      { min: 150, name: "맨하튼 야경", c1: "#0b1021", c2: "#1f2f5c", e: ["🛩️", "🚁", "🛸"], b: "🚀" },
      { min: 200, name: "화산 지대", c1: "#2b0000", c2: "#8a0303", e: ["🔥", "🦇", "☄️"], b: "🐉" },
      { min: 300, name: "사이버펑크", c1: "#0a0a2a", c2: "#3a0088", e: ["🤖", "⚙️", "👾"], b: "👁️‍🗨️" }
  ];

  // ★ 기존 가짜 데이터를 버리고 텅 빈 진짜 랭킹 시스템으로 교체!
  let highScores = JSON.parse(localStorage.getItem('7c_real_ranking')) || [];

  function checkCollision(x1, y1, r1, x2, y2, r2) {
      let dx = x1 - x2; let dy = y1 - y2;
      return Math.sqrt(dx*dx + dy*dy) < (r1 + r2);
  }

  function initBackground() {
      backgroundStars = [];
      for(let i=0; i<60; i++) {
          backgroundStars.push({ x: Math.random()*canvas.width, y: Math.random()*canvas.height, size: Math.random()*2+0.5, speed: Math.random()*4+1 });
      }
  }
  initBackground();

  function drawBackground() {
      let stg = stages[level - 1];
      let grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
      grad.addColorStop(0, stg.c1); grad.addColorStop(1, stg.c2);
      ctx.fillStyle = grad; ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.fillStyle = "rgba(255, 255, 255, 0.5)";
      for(let b of backgroundStars) {
          b.y += b.speed + (level * 1.5);
          if(b.y > canvas.height) { b.y = -10; b.x = Math.random()*canvas.width; }
          ctx.beginPath(); ctx.arc(b.x, b.y, b.size, 0, Math.PI*2); ctx.fill();
      }
  }

  function checkLevelUpdate() {
      let newLevel = 1;
      for (let i = stages.length - 1; i >= 0; i--) {
          if (score >= stages[i].min) { newLevel = i + 1; break; }
      }
      if (newLevel !== level) {
          level = newLevel;
          document.getElementById("stage-name").innerText = "📍 지역: " + stages[level - 1].name;
      }
  }

  function addEnergy(amount) {
      if(isLaserActive) return;
      energy += amount;
      if (energy >= 100) { energy = 100; useLaser(); }
      document.getElementById("energy-bar").style.width = energy + "%";
      document.getElementById("energy-text").innerText = Math.floor(energy) + "%";
  }

  function useBomb() {
      if (bombs > 0 && !gameOver) {
          bombs--; document.getElementById("bomb-ui").innerText = "💣 폭탄: " + bombs + "개";
          shockwaves.push({x: canvas.width/2, y: canvas.height/2, radius: 10, life: 30}); 
          for(let e of enemies) { createExplosion(e.x, e.y, "#FF4500", 25); score += e.hp; }
          enemies = []; enemyBullets = []; player.invincible = 60; // 1초 무적 부여
          checkLevelUpdate(); updateUI();
      }
  }

  function useLaser() {
      if (!gameOver && !isLaserActive) {
          energy = 0; document.getElementById("energy-bar").style.width = "0%";
          document.getElementById("energy-text").innerText = "⚠ 초고압 레이저 ⚠";
          isLaserActive = true; laserTimer = 100; player.invincible = 100; // 레이저 발사 중 무적 부여
      }
  }

  // 조작부
  let lastTap = 0;
  canvas.addEventListener('touchstart', function(e) {
      let currentTime = new Date().getTime();
      if (currentTime - lastTap < 300 && currentTime - lastTap > 0) { useBomb(); e.preventDefault(); }
      else { movePlayer(e.touches[0].clientX, e.touches[0].clientY, canvas.getBoundingClientRect()); }
      lastTap = currentTime;
  }, { passive: false });
  canvas.addEventListener('dblclick', function(e) { useBomb(); e.preventDefault(); });

  function createExplosion(x, y, color, count=15) {
      for(let i=0; i<count; i++) {
          particles.push({ x: x, y: y, vx: (Math.random()-0.5)*15, vy: (Math.random()-0.5)*15, size: Math.random()*4+2, color: color, life: 25 });
      }
  }

  function updateUI() {
      document.getElementById("score").innerText = "🏆 점수: " + score;
      document.getElementById("weapon").innerText = "⚡Lv." + weaponLevel;
  }

  // ★ 랭킹 등록 시스템 로직 ★
  function handleGameOver() {
      gameOver = true;
      document.getElementById("game-over-screen").style.display = "block";
      
      let isTop5 = false;
      if (score > 0) {
          // 순위표가 비어있거나 5명 미만이면 무조건 등록 가능!
          if (highScores.length < 5) {
              isTop5 = true;
          } 
          // 5명이 다 찼을 경우 꼴등 점수보다 높으면 등록 가능!
          else if (score > highScores[highScores.length - 1].score) {
              isTop5 = true;
          }
      }

      if (isTop5) {
          document.getElementById("new-record-input").style.display = "block";
          document.getElementById("leaderboard").style.display = "none";
          document.getElementById("initials").value = ""; // 입력창 초기화
      } else {
          document.getElementById("new-record-input").style.display = "none";
          showLeaderboard();
      }
  }

  function saveScore() {
      let initials = document.getElementById("initials").value.toUpperCase() || "UNK";
      highScores.push({name: initials.substring(0,3), score: score});
      highScores.sort((a,b) => b.score - a.score); // 점수 높은 순 정렬
      highScores = highScores.slice(0,5); // 딱 5명까지만 자르기
      
      // 내 스마트폰에 리얼 랭킹 저장!
      localStorage.setItem('7c_real_ranking', JSON.stringify(highScores));
      
      document.getElementById("new-record-input").style.display = "none";
      showLeaderboard();
  }

  function showLeaderboard() {
      let html = "";
      let colors = ["#FFD700", "#C0C0C0", "#CD7F32", "white", "gray"]; // 1,2,3등 메달색깔
      
      if (highScores.length === 0) {
          html = "<p style='text-align:center; color:gray;'>아직 등록된 랭킹이 없습니다.</p>";
      } else {
          highScores.forEach((s, idx) => {
              html += `<div class="rank-row" style="color:${colors[idx]};">
                          <span>${idx+1}위. ${s.name}</span>
                          <span>${s.score} 점</span>
                       </div>`;
          });
      }
      
      document.getElementById("leaderboard-list").innerHTML = html;
      document.getElementById("leaderboard").style.display = "block";
  }

  function update() {
      frameCount++; checkLevelUpdate();

      // ★ 불사신 버그 해결: 무적 시간이 알아서 닳아 없어지게 하는 마법의 코드 1줄 추가!
      if (player.invincible > 0) player.invincible--; 

      if (isLaserActive) {
          laserTimer--;
          let laserWidth = 70; let laserX = player.x - laserWidth/2;
          let gradient = ctx.createLinearGradient(laserX, 0, laserX + laserWidth, 0);
          gradient.addColorStop(0, "rgba(0, 255, 255, 0.2)"); gradient.addColorStop(0.5, "rgba(255, 255, 255, 0.9)"); gradient.addColorStop(1, "rgba(0, 255, 255, 0.2)");
          ctx.fillStyle = gradient; ctx.shadowBlur = 30; ctx.shadowColor = "cyan";
          ctx.fillRect(laserX, 0, laserWidth, player.y); ctx.shadowBlur = 0;

          for (let i = enemies.length - 1; i >= 0; i--) {
              if (enemies[i].x > laserX - enemies[i].radius && enemies[i].x < laserX + laserWidth + enemies[i].radius) {
                  createExplosion(enemies[i].x, enemies[i].y, "#00FFFF");
                  score += enemies[i].hp; enemies.splice(i, 1); updateUI();
              }
          }
          if (laserTimer <= 0) { isLaserActive = false; document.getElementById("energy-text").innerText = "0% (자동발사)"; }
      }

      if (frameCount % 10 === 0 && !isLaserActive) { 
          if (weaponLevel === 1) { bullets.push({x: player.x, y: player.y-20, color: '#FFD700', dx: 0}); } 
          else if (weaponLevel === 2) {
              bullets.push({x: player.x - 12, y: player.y-15, color: '#00FFFF', dx: 0});
              bullets.push({x: player.x + 12, y: player.y-15, color: '#00FFFF', dx: 0});
          } else {
              bullets.push({x: player.x, y: player.y-20, color: '#FF00FF', dx: 0});
              bullets.push({x: player.x - 15, y: player.y-10, color: '#FF00FF', dx: -2.5});
              bullets.push({x: player.x + 15, y: player.y-10, color: '#FF00FF', dx: 2.5});
          }
      }

      for (let i = bullets.length - 1; i >= 0; i--) {
          bullets[i].y -= 18; bullets[i].x += bullets[i].dx;
          if (bullets[i].y < 0) bullets.splice(i, 1);
      }

      let spawnRate = Math.max(15, 45 - Math.floor(score / 5));
      if (frameCount % spawnRate === 0) {
          let stg = stages[level - 1];
          let isBoss = Math.random() < 0.2;
          let emj = isBoss ? stg.b : stg.e[Math.floor(Math.random() * stg.e.length)];
          let hp = isBoss ? 6 : 2; let r = isBoss ? 25 : 18; let speed = isBoss ? 2 : 3.5;
          enemies.push({ x: Math.random()*(canvas.width-40)+20, y: -40, hp: hp, speed: speed, radius: r, emoji: emj, type: isBoss ? 'boss' : 'normal' });
      }

      for (let i = enemies.length - 1; i >= 0; i--) {
          let e = enemies[i];
          e.y += e.speed + (score / 200);
          
          if (e.type === 'boss' && frameCount % 70 === 0 && e.y > 0) {
              enemyBullets.push({ x: e.x, y: e.y, speed: 6, radius: 4 });
          }

          // ★ 플레이어와 적 생물체의 충돌 검사
          if (player.invincible <= 0 && checkCollision(player.x, player.y, 10, e.x, e.y, e.radius - 5)) {
              createExplosion(player.x, player.y, "#FF0000", 40);
              handleGameOver();
          }
          if (e.y > canvas.height + 30) enemies.splice(i, 1);
      }

      ctx.fillStyle = "#ff4d4d";
      for (let i = enemyBullets.length - 1; i >= 0; i--) {
          let eb = enemyBullets[i]; eb.y += eb.speed;
          ctx.shadowBlur = 10; ctx.shadowColor = "red";
          ctx.beginPath(); ctx.arc(eb.x, eb.y, eb.radius, 0, Math.PI*2); ctx.fill(); ctx.shadowBlur = 0;
          
          // ★ 플레이어와 적 미사일의 충돌 검사
          if (player.invincible <= 0 && checkCollision(player.x, player.y, 10, eb.x, eb.y, eb.radius)) {
              createExplosion(player.x, player.y, "#FF0000", 40);
              handleGameOver();
          }
          if (eb.y > canvas.height) enemyBullets.splice(i, 1);
      }

      for (let i = items.length - 1; i >= 0; i--) {
          let it = items[i]; it.y += 3.5;
          if (checkCollision(player.x, player.y, player.radius, it.x, it.y, 15)) {
              items.splice(i, 1);
              if (weaponLevel < 3) weaponLevel++;
              updateUI(); continue;
          }
          if (it.y > canvas.height) items.splice(i, 1);
      }

      for (let i = enemies.length - 1; i >= 0; i--) {
          let hit = false;
          for (let j = bullets.length - 1; j >= 0; j--) {
              if (checkCollision(bullets[j].x, bullets[j].y, 3, enemies[i].x, enemies[i].y, enemies[i].radius)) {
                  bullets.splice(j, 1); enemies[i].hp--; hit = true; break;
              }
          }
          if (hit) {
              if (enemies[i].hp <= 0) {
                  createExplosion(enemies[i].x, enemies[i].y, "#FFD700", 20);
                  if (Math.random() < 0.12) items.push({ x: enemies[i].x, y: enemies[i].y }); 
                  let gainedEnergy = (enemies[i].type === 'boss') ? 18 : 6; addEnergy(gainedEnergy);
                  score += 1; enemies.splice(i, 1); updateUI();
              } else {
                  createExplosion(enemies[i].x, enemies[i].y, "white", 4); 
              }
          }
      }
  }

  function gameLoop() {
      if (gameOver) return; 
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      drawBackground();
      update();
      
      for (let i = particles.length - 1; i >= 0; i--) {
          let p = particles[i];
          ctx.fillStyle = p.color; ctx.globalAlpha = p.life / 25;
          ctx.beginPath(); ctx.arc(p.x, p.y, p.size, 0, Math.PI*2); ctx.fill(); ctx.globalAlpha = 1.0;
          p.x += p.vx; p.y += p.vy; p.life--; if (p.life <= 0) particles.splice(i, 1);
      }
      for(let i=shockwaves.length-1; i>=0; i--) {
          let sw = shockwaves[i];
          ctx.strokeStyle = `rgba(0, 255, 255, ${sw.life/30})`; ctx.lineWidth = 15;
          ctx.beginPath(); ctx.arc(sw.x, sw.y, sw.radius, 0, Math.PI*2); ctx.stroke();
          sw.radius += 25; sw.life--; if(sw.life <=0) shockwaves.splice(i,1);
      }
      
      ctx.textAlign = "center"; ctx.textBaseline = "middle";
      
      for (let e of enemies) {
          ctx.font = (e.radius * 2 - 10) + "px Arial";
          ctx.fillText(e.emoji, e.x, e.y);
      }
      for (let item of items) {
          ctx.font = "25px Arial"; ctx.fillText("⭐", item.x, item.y);
      }
      
      for (let b of bullets) {
          ctx.shadowBlur = 15; ctx.shadowColor = b.color;
          ctx.fillStyle = "white"; ctx.beginPath();
          ctx.ellipse(b.x, b.y, 3.5, 14, 0, 0, Math.PI*2); ctx.fill(); ctx.shadowBlur = 0;
      }
      
      // 내 비행기 깜빡임(무적) 효과
      if (player.invincible <= 0 || (frameCount % 6 < 3)) {
          ctx.fillStyle = (frameCount % 4 < 2) ? "#FF4500" : "#FFD700";
          ctx.beginPath(); ctx.arc(player.x, player.y + 20, Math.random()*4+4, 0, Math.PI*2); ctx.fill();
          
          ctx.save();
          ctx.translate(player.x, player.y);
          ctx.rotate(-45 * Math.PI / 180);
          ctx.font = "40px Arial"; 
          ctx.fillText(player.emoji, 0, 0);
          ctx.restore();
      }
      
      requestAnimationFrame(gameLoop);
  }

  function movePlayer(clientX, clientY, rect) {
      player.x = clientX - rect.left; player.y = clientY - rect.top;
      if (player.x < 15) player.x = 15;
      if (player.x > canvas.width - 15) player.x = canvas.width - 15;
      if (player.y < 15) player.y = 15;
      if (player.y > canvas.height - 15) player.y = canvas.height - 15;
  }

  canvas.addEventListener("touchmove", function(e) {
      e.preventDefault(); movePlayer(e.touches[0].clientX, e.touches[0].clientY, canvas.getBoundingClientRect());
  }, { passive: false });
  canvas.addEventListener("mousemove", function(e) { movePlayer(e.clientX, e.clientY, canvas.getBoundingClientRect()); });

  function resetGame() {
      score = 0; level = 1; energy = 0; bombs = 2; weaponLevel = 1; gameOver = false; frameCount = 0; isLaserActive = false;
      bullets = []; enemyBullets = []; enemies = []; items = []; particles = []; shockwaves = [];
      player.x = 175; player.y = 400; player.invincible = 0;
      document.getElementById("bomb-ui").innerText = "💣 폭탄: 2개";
      document.getElementById("stage-name").innerText = "📍 지역: 우주 궤도";
      document.getElementById("game-over-screen").style.display = "none";
      initBackground(); addEnergy(0); updateUI(); gameLoop();
  }

  resetGame();
</script>
</body>
</html>
"""

components.html(game_html, height=750)
