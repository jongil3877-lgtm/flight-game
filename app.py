import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="7C 비행 슈팅 V2", page_icon="✈️", layout="centered")

st.title("🔥 7C 비행 슈팅: 하드코어 모드")
st.markdown("그래픽과 난이도가 대폭 상승했습니다! **모함(🛸)**은 3방을 맞아야 터집니다. 쏟아지는 **운석(☄️)**을 조심하세요!")
st.markdown("---")

game_html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  body { display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 0; touch-action: none; background-color: #111; color: white;}
  canvas { background: #000010; border-radius: 10px; box-shadow: 0 0 20px rgba(0, 150, 255, 0.5); border: 2px solid #333; }
  #score-board { font-size: 20px; font-family: 'Arial', sans-serif; font-weight: bold; margin-bottom: 10px; display: flex; justify-content: space-between; width: 350px; }
  #game-over { color: #FF4B4B; font-size: 28px; font-weight: bold; display: none; margin-top: 15px; text-align: center; text-shadow: 0 0 10px red; }
  #btn-restart { margin-top: 15px; padding: 12px 24px; font-size: 18px; cursor: pointer; background: #FF4B4B; color: white; border: none; border-radius: 8px; display: none; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.5); }
</style>
</head>
<body>
  <div id="score-board">
      <span id="score" style="color: #FFD700;">💥 격추: 0 기</span>
      <span id="weapon" style="color: #00FFFF;">⚡ 무기: Lv.1</span>
  </div>
  <canvas id="gameCanvas" width="350" height="500"></canvas>
  <div id="game-over">🔥 추락했습니다!</div>
  <button id="btn-restart" onclick="resetGame()">🔄 다시 출격하기</button>

<script>
  const canvas = document.getElementById("gameCanvas");
  const ctx = canvas.getContext("2d");
  let score = 0;
  let gameOver = false;
  let weaponLevel = 1;
  let frameCount = 0;
  let animationId;

  const player = { x: 155, y: 420, width: 40, height: 40, emoji: "✈️" };
  let bullets = [];
  let enemies = [];
  let items = [];
  let particles = [];
  let stars = [];

  // 우주 배경 별자리 초기화
  for(let i=0; i<70; i++) {
      stars.push({x: Math.random()*canvas.width, y: Math.random()*canvas.height, size: Math.random()*2.5, speed: Math.random()*3+1});
  }

  function drawStars() {
      ctx.fillStyle = "white";
      for(let s of stars) {
          s.y += s.speed + (score/150); // 점수 높을수록 배경이 빨리 지나감 (광속 효과)
          if(s.y > canvas.height) { s.y = 0; s.x = Math.random()*canvas.width; }
          ctx.beginPath();
          ctx.arc(s.x, s.y, s.size/2, 0, Math.PI*2);
          ctx.fill();
      }
  }

  function drawPlayer() {
      // 엔진 불꽃 효과
      ctx.fillStyle = (frameCount % 4 < 2) ? "#FF4500" : "#FFD700";
      ctx.beginPath();
      ctx.arc(player.x + 20, player.y + 45, Math.random() * 8 + 5, 0, Math.PI*2);
      ctx.fill();

      // 삐딱한 이모티콘 똑바로 세우기 (-45도 회전 마법)
      ctx.save();
      ctx.translate(player.x + 20, player.y + 20);
      ctx.rotate(-45 * Math.PI / 180);
      ctx.font = "45px Arial";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(player.emoji, 0, 0);
      ctx.restore();
  }

  function drawBullets() {
      for (let b of bullets) {
          ctx.shadowBlur = 10;
          ctx.shadowColor = b.color;
          ctx.fillStyle = "white";
          ctx.beginPath();
          ctx.ellipse(b.x, b.y, 3, 12, 0, 0, Math.PI*2); // 동그라미가 아닌 레이저 빔 형태
          ctx.fill();
          ctx.shadowBlur = 0;
      }
  }

  function drawParticles() {
      for (let i = particles.length - 1; i >= 0; i--) {
          let p = particles[i];
          ctx.fillStyle = p.color;
          ctx.globalAlpha = p.life / 20;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size, 0, Math.PI*2);
          ctx.fill();
          ctx.globalAlpha = 1.0;
          
          p.x += p.vx;
          p.y += p.vy;
          p.life--;
          if (p.life <= 0) particles.splice(i, 1);
      }
  }

  function createExplosion(x, y, color) {
      for(let i=0; i<15; i++) {
          particles.push({
              x: x + 15, y: y + 15,
              vx: (Math.random() - 0.5) * 10,
              vy: (Math.random() - 0.5) * 10,
              size: Math.random() * 4 + 2,
              color: color,
              life: 20
          });
      }
  }

  function update() {
      frameCount++;
      
      // 🚀 무기 발사 (발사 속도 상향)
      if (frameCount % 10 === 0) { 
          if (weaponLevel === 1) {
              bullets.push({x: player.x + 20, y: player.y, color: '#FFD700', dx: 0});
          } else if (weaponLevel === 2) {
              bullets.push({x: player.x + 8, y: player.y + 10, color: '#00FFFF', dx: 0});
              bullets.push({x: player.x + 32, y: player.y + 10, color: '#00FFFF', dx: 0});
          } else {
              bullets.push({x: player.x + 20, y: player.y - 10, color: '#FF00FF', dx: 0});
              bullets.push({x: player.x + 5, y: player.y + 10, color: '#FF00FF', dx: -1.5});
              bullets.push({x: player.x + 35, y: player.y + 10, color: '#FF00FF', dx: 1.5});
          }
      }

      for (let i = bullets.length - 1; i >= 0; i--) {
          bullets[i].y -= 15; // 미사일 속도 증가
          bullets[i].x += bullets[i].dx;
          if (bullets[i].y < 0) bullets.splice(i, 1);
      }

      // 👾 적군 출현 (점수에 따라 미친듯이 쏟아짐)
      let spawnRate = Math.max(10, 45 - Math.floor(score / 4));
      if (frameCount % spawnRate === 0) {
          let r = Math.random();
          if (r < 0.2) {
              enemies.push({ x: Math.random() * (canvas.width - 40), y: -40, emoji: "☄️", hp: 1, speed: 8 }); // 초고속 운석
          } else if (r < 0.4) {
              enemies.push({ x: Math.random() * (canvas.width - 40), y: -40, emoji: "🛸", hp: 3, speed: 2 }); // 체력 3 모함
          } else {
              enemies.push({ x: Math.random() * (canvas.width - 40), y: -40, emoji: "👾", hp: 1, speed: 4 }); // 일반
          }
      }

      // 적 이동 및 충돌
      for (let i = enemies.length - 1; i >= 0; i--) {
          enemies[i].y += enemies[i].speed + (score / 80);
          
          // 플레이어와 충돌 (히트박스 정밀화)
          if (player.x + 10 < enemies[i].x + 30 && player.x + 30 > enemies[i].x &&
              player.y + 10 < enemies[i].y + 30 && player.y + 30 > enemies[i].y) {
              createExplosion(player.x, player.y, "#FF0000");
              gameOver = true;
          }

          if (enemies[i].y > canvas.height) enemies.splice(i, 1);
      }

      // ⭐ 아이템 이동 및 획득
      for (let i = items.length - 1; i >= 0; i--) {
          items[i].y += 4;
          if (player.x < items[i].x + 25 && player.x + 35 > items[i].x &&
              player.y < items[i].y + 25 && player.y + 35 > items[i].y) {
              items.splice(i, 1);
              if (weaponLevel < 3) weaponLevel++;
              document.getElementById("weapon").innerText = "⚡ 무기: Lv." + weaponLevel;
              continue;
          }
          if (items[i].y > canvas.height) items.splice(i, 1);
      }

      // 💥 충돌 판정 (적 vs 미사일)
      for (let i = enemies.length - 1; i >= 0; i--) {
          let hit = false;
          for (let j = bullets.length - 1; j >= 0; j--) {
              if (bullets[j].x > enemies[i].x && bullets[j].x < enemies[i].x + 35 &&
                  bullets[j].y > enemies[i].y && bullets[j].y < enemies[i].y + 35) {
                  
                  bullets.splice(j, 1);
                  enemies[i].hp--; // 체력 감소
                  
                  if(enemies[i].hp <= 0) {
                      hit = true;
                  } else {
                      // 맞았지만 안 죽었을 때 작은 파편
                      createExplosion(enemies[i].x, enemies[i].y, "white");
                  }
                  break;
              }
          }
          if (hit) {
              createExplosion(enemies[i].x, enemies[i].y, "#FFD700"); // 화려한 폭발!
              
              if (Math.random() < 0.08) { // 8% 확률로 아이템 드롭
                  items.push({ x: enemies[i].x, y: enemies[i].y });
              }
              enemies.splice(i, 1);
              score += 1;
              document.getElementById("score").innerText = "💥 격추: " + score + " 기";
          }
      }
  }

  function gameLoop() {
      if (gameOver) {
          document.getElementById("game-over").style.display = "block";
          document.getElementById("btn-restart").style.display = "block";
          return;
      }

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      drawStars(); // 배경 먼저
      update(); // 데이터 업데이트
      drawParticles(); // 폭발 효과
      
      // 적, 아이템, 플레이어 그리기
      ctx.font = "35px Arial";
      ctx.textAlign = "left";
      ctx.textBaseline = "alphabetic";
      for (let e of enemies) ctx.fillText(e.emoji, e.x, e.y + 30);
      for (let item of items) ctx.fillText("⭐", item.x, item.y + 25);
      
      drawBullets();
      drawPlayer(); // 비행기를 제일 마지막에 (가장 위로)

      animationId = requestAnimationFrame(gameLoop);
  }

  // 조작부
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
      score = 0;
      gameOver = false;
      weaponLevel = 1;
      frameCount = 0;
      bullets = [];
      enemies = [];
      items = [];
      particles = [];
      player.x = 155;
      player.y = 420;
      document.getElementById("score").innerText = "💥 격추: 0 기";
      document.getElementById("weapon").innerText = "⚡ 무기: Lv.1";
      document.getElementById("game-over").style.display = "none";
      document.getElementById("btn-restart").style.display = "none";
      gameLoop();
  }

  resetGame();
</script>
</body>
</html>
"""

components.html(game_html, height=650)
