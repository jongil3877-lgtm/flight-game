import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="7C 비행 슈팅 끝판왕", page_icon="✈️", layout="centered")

st.title("🌊 7C 슈팅: 바다의 지배자")
st.markdown("점수가 **100점**을 넘으면 **바다 스테이지**로 진입합니다! 함대(🚢)가 미사일을 쏘니 주의하세요. \n* 💣**필살기:** 화면 전체 폭격! \n* ⚡**레이저:** 에너지가 100% 차면 버튼을 눌러 적을 쓸어버리세요!")
st.markdown("---")

game_html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  body { display: flex; flex-direction: column; align-items: center; background-color: #111; color: white; margin: 0; padding: 10px; touch-action: none; font-family: 'Arial', sans-serif;}
  canvas { border-radius: 10px; box-shadow: 0 0 20px rgba(0, 150, 255, 0.5); border: 2px solid #555; }
  
  .status-bar { width: 350px; display: flex; justify-content: space-between; font-weight: bold; font-size: 18px; margin-bottom: 5px; }
  .energy-container { width: 350px; height: 15px; background: #333; border-radius: 10px; margin-bottom: 10px; border: 1px solid #fff; position: relative;}
  #energy-bar { height: 100%; width: 0%; background: linear-gradient(90deg, #00ffff, #ff00ff); border-radius: 10px; transition: width 0.2s; }
  #energy-text { position: absolute; top: -2px; left: 45%; font-size: 12px; font-weight: bold; }

  .btn-group { display: flex; gap: 10px; width: 350px; margin-top: 15px; }
  .skill-btn { flex: 1; padding: 15px 0; font-size: 18px; font-weight: bold; border: none; border-radius: 10px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.5); }
  #btn-bomb { background: #FF4500; color: white; }
  #btn-laser { background: #555; color: white; } /* 비활성화 색상 */
  #btn-laser.active { background: #00FFFF; color: black; box-shadow: 0 0 15px cyan; animation: blink 1s infinite;}
  
  @keyframes blink { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }

  #game-over-screen { position: absolute; top: 250px; text-align: center; display: none; width: 350px;}
  #game-over-text { color: #FF4B4B; font-size: 32px; font-weight: bold; text-shadow: 0 0 15px red; margin-bottom: 20px;}
  #btn-restart { padding: 12px 24px; font-size: 20px; font-weight: bold; background: #FF4B4B; color: white; border: none; border-radius: 8px; cursor: pointer; }
</style>
</head>
<body>
  
  <div class="status-bar">
      <span id="score" style="color: #FFD700;">점수: 0</span>
      <span id="weapon" style="color: #00FFFF;">⚡무기: Lv.1</span>
  </div>
  
  <div class="energy-container">
      <div id="energy-bar"></div>
      <span id="energy-text">0%</span>
  </div>

  <canvas id="gameCanvas" width="350" height="480"></canvas>
  
  <div class="btn-group">
      <button id="btn-bomb" class="skill-btn" onclick="useBomb()">💣 폭격 (<span id="bomb-count">2</span>)</button>
      <button id="btn-laser" class="skill-btn" onclick="useLaser()">⚡ 레이저 발사!</button>
  </div>

  <div id="game-over-screen">
      <div id="game-over-text">🔥 추락했습니다!</div>
      <button id="btn-restart" onclick="resetGame()">🔄 다시 출격</button>
  </div>

<script>
  const canvas = document.getElementById("gameCanvas");
  const ctx = canvas.getContext("2d");
  
  let score = 0;
  let level = 1; // 1: 우주, 2: 바다
  let energy = 0;
  let bombs = 2;
  let weaponLevel = 1;
  let gameOver = false;
  let frameCount = 0;
  
  // 레이저 관련
  let isLaserActive = false;
  let laserTimer = 0;

  const player = { x: 155, y: 400, width: 40, height: 40, emoji: "✈️", invincible: 0 };
  let bullets = [];
  let enemyBullets = [];
  let enemies = [];
  let items = [];
  let particles = [];
  let backgroundItems = []; // 별 or 파도

  // 배경 요소 초기화
  function initBackground() {
      backgroundItems = [];
      for(let i=0; i<40; i++) {
          backgroundItems.push({
              x: Math.random() * canvas.width, 
              y: Math.random() * canvas.height, 
              size: Math.random() * 2 + 1, 
              speed: Math.random() * 3 + 1
          });
      }
  }
  initBackground();

  function drawBackground() {
      if (level === 1) {
          ctx.fillStyle = "#000015"; // 우주 배경
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          ctx.fillStyle = "white";
          for(let b of backgroundItems) {
              b.y += b.speed + (score/200);
              if(b.y > canvas.height) { b.y = 0; b.x = Math.random()*canvas.width; }
              ctx.beginPath(); ctx.arc(b.x, b.y, b.size, 0, Math.PI*2); ctx.fill();
          }
      } else {
          ctx.fillStyle = "#004466"; // 바다 배경
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          ctx.font = "20px Arial";
          for(let b of backgroundItems) {
              b.y += b.speed + 1;
              if(b.y > canvas.height) { b.y = 0; b.x = Math.random()*canvas.width; }
              ctx.fillText("〰️", b.x, b.y); // 물결
          }
      }
  }

  function addEnergy(amount) {
      if(isLaserActive) return;
      energy += amount;
      if (energy >= 100) {
          energy = 100;
          document.getElementById("btn-laser").classList.add("active");
      }
      document.getElementById("energy-bar").style.width = energy + "%";
      document.getElementById("energy-text").innerText = Math.floor(energy) + "%";
  }

  function useBomb() {
      if (bombs > 0 && !gameOver) {
          bombs--;
          document.getElementById("bomb-count").innerText = bombs;
          // 화면 전체 적 파괴
          for(let e of enemies) {
              createExplosion(e.x, e.y, "#FF4500", 30);
              score += e.hp;
          }
          enemies = [];
          enemyBullets = []; // 적 총알도 소거
          player.invincible = 60; // 1초 무적
          
          // 화면 번쩍임 효과
          ctx.fillStyle = "white";
          ctx.fillRect(0,0,canvas.width,canvas.height);
          updateUI();
      }
  }

  function useLaser() {
      if (energy >= 100 && !gameOver && !isLaserActive) {
          energy = 0;
          document.getElementById("btn-laser").classList.remove("active");
          addEnergy(0); // UI 업데이트
          isLaserActive = true;
          laserTimer = 90; // 약 1.5초간 레이저 발사
          player.invincible = 90; // 레이저 쏘는 동안 무적
      }
  }

  function createExplosion(x, y, color, count=15) {
      for(let i=0; i<count; i++) {
          particles.push({
              x: x + 15, y: y + 15,
              vx: (Math.random() - 0.5) * 12, vy: (Math.random() - 0.5) * 12,
              size: Math.random() * 5 + 2, color: color, life: 25
          });
      }
  }

  function drawParticles() {
      for (let i = particles.length - 1; i >= 0; i--) {
          let p = particles[i];
          ctx.fillStyle = p.color;
          ctx.globalAlpha = p.life / 25;
          ctx.beginPath(); ctx.arc(p.x, p.y, p.size, 0, Math.PI*2); ctx.fill();
          ctx.globalAlpha = 1.0;
          p.x += p.vx; p.y += p.vy; p.life--;
          if (p.life <= 0) particles.splice(i, 1);
      }
  }

  function drawPlayer() {
      if (player.invincible > 0) {
          player.invincible--;
          if (frameCount % 6 < 3) return; // 무적일 때 깜빡거림 효과
      }
      
      // 엔진 불꽃
      ctx.fillStyle = (frameCount % 4 < 2) ? "#FF4500" : "#FFD700";
      ctx.beginPath(); ctx.arc(player.x + 20, player.y + 45, Math.random() * 8 + 5, 0, Math.PI*2); ctx.fill();

      // 비행기 똑바로 세워서 그리기
      ctx.save();
      ctx.translate(player.x + 20, player.y + 20);
      ctx.rotate(-45 * Math.PI / 180);
      ctx.font = "45px Arial"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
      ctx.fillText(player.emoji, 0, 0);
      ctx.restore();
  }

  function updateUI() {
      document.getElementById("score").innerText = "점수: " + score;
      document.getElementById("weapon").innerText = "⚡무기: Lv." + weaponLevel;
  }

  function update() {
      frameCount++;
      
      // 스테이지 전환 (100점 돌파 시 Бада로!)
      if (score >= 100 && level === 1) {
          level = 2;
          initBackground();
      }

      // ⚡ 레이저 빔 로직
      if (isLaserActive) {
          laserTimer--;
          ctx.fillStyle = "rgba(0, 255, 255, 0.8)";
          ctx.shadowBlur = 20; ctx.shadowColor = "cyan";
          // 비행기 앞에서부터 화면 끝까지 거대한 사각형 빔
          ctx.fillRect(player.x - 10, 0, 60, player.y + 10);
          ctx.shadowBlur = 0;

          // 레이저에 닿은 적 즉사
          for (let i = enemies.length - 1; i >= 0; i--) {
              if (enemies[i].x + 30 > player.x - 10 && enemies[i].x < player.x + 50) {
                  createExplosion(enemies[i].x, enemies[i].y, "#00FFFF");
                  score += enemies[i].hp;
                  enemies.splice(i, 1);
                  updateUI();
              }
          }
          if (laserTimer <= 0) isLaserActive = false;
      }

      // 🚀 기본 미사일 발사 (레이저 쏘는 중엔 중지)
      if (frameCount % 10 === 0 && !isLaserActive) { 
          if (weaponLevel === 1) {
              bullets.push({x: player.x + 20, y: player.y, color: '#FFD700', dx: 0});
          } else if (weaponLevel === 2) {
              bullets.push({x: player.x + 8, y: player.y, color: '#00FFFF', dx: 0});
              bullets.push({x: player.x + 32, y: player.y, color: '#00FFFF', dx: 0});
          } else {
              bullets.push({x: player.x + 20, y: player.y - 10, color: '#FF00FF', dx: 0});
              bullets.push({x: player.x + 5, y: player.y + 10, color: '#FF00FF', dx: -2});
              bullets.push({x: player.x + 35, y: player.y + 10, color: '#FF00FF', dx: 2});
          }
      }

      for (let i = bullets.length - 1; i >= 0; i--) {
          bullets[i].y -= 15; bullets[i].x += bullets[i].dx;
          if (bullets[i].y < 0) bullets.splice(i, 1);
      }

      // 👾 적군 출현
      let spawnRate = Math.max(12, 45 - Math.floor(score / 4));
      if (frameCount % spawnRate === 0) {
          let r = Math.random();
          if (level === 1) {
              // 1스테이지 우주
              if (r < 0.2) enemies.push({ x: Math.random() * (canvas.width - 40), y: -40, emoji: "☄️", hp: 1, speed: 7, type: 'meteor' });
              else if (r < 0.4) enemies.push({ x: Math.random() * (canvas.width - 40), y: -40, emoji: "🛸", hp: 4, speed: 1.5, type: 'boss' });
              else enemies.push({ x: Math.random() * (canvas.width - 40), y: -40, emoji: "👾", hp: 1, speed: 3.5, type: 'normal' });
          } else {
              // 2스테이지 바다 (배 등장)
              if (r < 0.3) enemies.push({ x: Math.random() * (canvas.width - 40), y: -40, emoji: "🚢", hp: 6, speed: 1, type: 'ship' }); // 튼튼한 배
              else if (r < 0.5) enemies.push({ x: Math.random() * (canvas.width - 40), y: -40, emoji: "🚁", hp: 2, speed: 4, type: 'normal' });
              else enemies.push({ x: Math.random() * (canvas.width - 40), y: -40, emoji: "🛩️", hp: 1, speed: 5, type: 'normal' });
          }
      }

      // 적 이동 및 공격
      for (let i = enemies.length - 1; i >= 0; i--) {
          let e = enemies[i];
          e.y += e.speed + (score / 100);
          
          // 배(🚢)나 보스(🛸)는 플레이어를 향해 총알을 쏩니다!
          if ((e.type === 'ship' || e.type === 'boss') && frameCount % 80 === 0 && e.y > 0) {
              enemyBullets.push({ x: e.x + 20, y: e.y + 30, speed: 5 });
          }

          // 플레이어 충돌
          if (player.invincible <= 0 && 
              player.x + 10 < e.x + 30 && player.x + 30 > e.x &&
              player.y + 10 < e.y + 30 && player.y + 30 > e.y) {
              createExplosion(player.x, player.y, "#FF0000", 30);
              gameOver = true;
          }
          if (e.y > canvas.height) enemies.splice(i, 1);
      }

      // 적의 총알 이동 및 충돌
      ctx.fillStyle = "red";
      for (let i = enemyBullets.length - 1; i >= 0; i--) {
          let eb = enemyBullets[i];
          eb.y += eb.speed;
          ctx.beginPath(); ctx.arc(eb.x, eb.y, 5, 0, Math.PI*2); ctx.fill();
          
          if (player.invincible <= 0 &&
              eb.x > player.x && eb.x < player.x + 40 &&
              eb.y > player.y && eb.y < player.y + 40) {
              createExplosion(player.x, player.y, "#FF0000", 30);
              gameOver = true;
          }
          if (eb.y > canvas.height) enemyBullets.splice(i, 1);
      }

      // ⭐ 아이템 이동 및 획득
      for (let i = items.length - 1; i >= 0; i--) {
          items[i].y += 3;
          if (player.x < items[i].x + 25 && player.x + 35 > items[i].x &&
              player.y < items[i].y + 25 && player.y + 35 > items[i].y) {
              items.splice(i, 1);
              if (weaponLevel < 3) weaponLevel++;
              updateUI();
              continue;
          }
          if (items[i].y > canvas.height) items.splice(i, 1);
      }

      // 💥 내 미사일이 적을 맞췄을 때
      for (let i = enemies.length - 1; i >= 0; i--) {
          let hit = false;
          for (let j = bullets.length - 1; j >= 0; j--) {
              if (bullets[j].x > enemies[i].x && bullets[j].x < enemies[i].x + 40 &&
                  bullets[j].y > enemies[i].y && bullets[j].y < enemies[i].y + 40) {
                  bullets.splice(j, 1);
                  enemies[i].hp--;
                  hit = true;
                  break;
              }
          }
          if (hit) {
              if (enemies[i].hp <= 0) {
                  createExplosion(enemies[i].x, enemies[i].y, "#FFD700");
                  if (Math.random() < 0.1) items.push({ x: enemies[i].x, y: enemies[i].y }); // 10% 아이템
                  
                  // 에너지 충전 (배나 보스를 잡으면 더 많이 줌)
                  let gainedEnergy = (enemies[i].type === 'ship' || enemies[i].type === 'boss') ? 15 : 5;
                  addEnergy(gainedEnergy);
                  
                  score += 1;
                  enemies.splice(i, 1);
                  updateUI();
              } else {
                  createExplosion(enemies[i].x, enemies[i].y, "white", 3); // 타격 파편
              }
          }
      }
  }

  function gameLoop() {
      if (gameOver) {
          document.getElementById("game-over-screen").style.display = "block";
          return;
      }

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      drawBackground();
      update();
      drawParticles();
      
      ctx.font = "35px Arial"; ctx.textAlign = "left"; ctx.textBaseline = "alphabetic";
      for (let e of enemies) ctx.fillText(e.emoji, e.x, e.y + 30);
      for (let item of items) ctx.fillText("⭐", item.x, item.y + 25);
      
      for (let b of bullets) {
          ctx.shadowBlur = 10; ctx.shadowColor = b.color;
          ctx.fillStyle = "white"; ctx.beginPath();
          ctx.ellipse(b.x, b.y, 3, 12, 0, 0, Math.PI*2); ctx.fill();
          ctx.shadowBlur = 0;
      }
      
      drawPlayer();
      requestAnimationFrame(gameLoop);
  }

  function movePlayer(clientX, clientY, rect) {
      player.x = clientX - rect.left - player.width / 2;
      player.y = clientY - rect.top - player.height / 2;
      if (player.x < -10) player.x = -10;
      if (player.x + player.width > canvas.width + 10) player.x = canvas.width - player.width + 10;
      if (player.y < 0) player.y = 0;
      if (player.y + player.height > canvas.height) player.y = canvas.height - player.height;
  }

  canvas.addEventListener("touchmove", function(e) {
      e.preventDefault();
      movePlayer(e.touches[0].clientX, e.touches[0].clientY, canvas.getBoundingClientRect());
  }, { passive: false });

  canvas.addEventListener("mousemove", function(e) {
      movePlayer(e.clientX, e.clientY, canvas.getBoundingClientRect());
  });

  function resetGame() {
      score = 0; level = 1; energy = 0; bombs = 2; weaponLevel = 1; gameOver = false; frameCount = 0; isLaserActive = false;
      bullets = []; enemyBullets = []; enemies = []; items = []; particles = [];
      player.x = 155; player.y = 400; player.invincible = 0;
      document.getElementById("bomb-count").innerText = bombs;
      document.getElementById("game-over-screen").style.display = "none";
      initBackground();
      addEnergy(0);
      updateUI();
      gameLoop();
  }

  resetGame();
</script>
</body>
</html>
"""

components.html(game_html, height=750)
