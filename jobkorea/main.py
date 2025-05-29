from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

def sub_crawl(df,driver,url_list):
    
    for i in url_list:
        try:
            company_name=""
            address=""
            kind=""
            year=""
            people=""
            homepage=""

            driver.get("https://www.jobkorea.co.kr"+i)
            time.sleep(3)
            
            print(driver.current_url)
            company_name=driver.find_element(By.CLASS_NAME, "coName").text
            tag = driver.find_element(By.CLASS_NAME,"tbCoInfo").find_element(By.CLASS_NAME, "tbList").find_elements(By.TAG_NAME,"dt")
            info = driver.find_element(By.CLASS_NAME,"tbCoInfo").find_element(By.CLASS_NAME, "tbList").find_elements(By.TAG_NAME,"dd")
            for i in range(0,len(tag)):
                if "업종" in tag[i].text:
                    kind=info[i].text
                elif "설립년도" in tag[i].text:
                    year=info[i].text   
                elif "사원수" in tag[i].text:
                    people=info[i].text
                elif "홈페이지" in tag[i].text:
                    homepage=info[i].text
            tag = driver.find_element(By.CLASS_NAME,"artReadJobSum").find_elements(By.CLASS_NAME, "tbList")[1].find_elements(By.TAG_NAME,"dt")
            info = driver.find_element(By.CLASS_NAME,"artReadJobSum").find_elements(By.CLASS_NAME, "tbList")[1].find_elements(By.TAG_NAME,"dd")
            for i in range(0,len(tag)):
                if "지역" in tag[i].text:
                    address=info[i].text.replace("지도","")
            manager=""
            department=""
            phone=""
            fax=""
            email=""
            try:
                element=driver.find_element(By.CLASS_NAME, "devOpenCharge")
                driver.execute_script("arguments[0].click();", element)
            except:
                pass
            try:
                m=driver.find_element(By.CLASS_NAME,"manager").text
                if "인사 담당자" in m:
                    manager=m.split("부서명")[0].split("인사 담당자")[1].split("연락처")[0].split("팩스")[0].split("e-메일")[0]
                if "부서명" in m:
                    department=m.split("연락처")[0].split("부서명")[1].split("팩스")[0].split("e-메일")[0]
                if "연락처" in m:
                    phone=m.split("연락처")[1].split("팩스")[0].split("e-메일")[0]
                if "팩스" in m:
                    fax=m.split("팩스")[1]
                if "e-메일" in m:
                    email=m.split("e-메일")[1]

                if"연락처" in department:
                    department=""
            except:
                m=""
            title=driver.find_element(By.CLASS_NAME,"sumTit").text
            title=title.split("닫기")
            title=title[1]
            url=driver.current_url
            print(title)
            print(manager)
            print(department)
            print(address)
            # ["회사명","업종","주소","설립","매출액","사원수","홈페이지","담당자","부서명","연락처","이메일","팩스","공고 제목","공고 url"]
            new_row={"회사명":company_name,"업종":kind,"주소":address,"설립":year,"매출액":"","사원수":people,"홈페이지":homepage,"담당자":manager,"부서명":department,"연락처":phone,"이메일":email,"팩스":fax,"공고 제목":title,"공고 url":url}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        except NoSuchElementException:
            continue
        except:
            print("url수집중 에러가 발생했습니다. 프로그램을 다시 실행 해주세요.")
            continue

    return df

def get_chromedriver(headless: bool = False) -> webdriver.Chrome:
    # Set Chrome options
    options = Options()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")

    # Use WebDriver Manager to get the right driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver

def export_to_excel(df):
    df.to_excel('output.xlsx')

def login(driver):
    driver.get("https://www.jobkorea.co.kr/Login")
    print("잡코리아 로그인이 필요합니다. 로그인 창에서 아이디, 비밀번호를 입력해 주세요.")
    print("로그인이 끝나면 아무 숫자나 입력 후 enter을 눌러주세요.")
    a=input()
    print("로그인 과정이 끝났습니다.")

def crawl_jobkorea():
    
    driver=get_chromedriver()
    login(driver)
    print("크롤링 하실 최대 페이지 개수를 입력해주세요.")
    t=input()
    t=int(t)
    t+=2
    print("키워드 검색을 하시려면 1, 지역별 검색을 하시려면 2를 누르고 엔터를 눌러주세요.")
    a=input()
    a=int(a)
    idx=0
    df = pd.DataFrame(columns=["회사명","업종","주소","설립","매출액","사원수","홈페이지","담당자","부서명","연락처","이메일","팩스","공고 제목","공고 url"])
    recruit_url_list=[]
    if a==1:
        print("키워드를 입력하고 엔터를 눌러주세요.")
        a=input()
        while True:
            if idx==t:
                break
            time.sleep(0.5)
            idx+=1
            headers = {
                'Accept': 'text/html, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8,ja;q=0.7',
                'Connection': 'keep-alive',
                'Referer': 'https://www.jobkorea.co.kr/Search/?stext=%EB%83%89%EB%8F%99&tabType=recruit&Page_No=3',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest',
                'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                # 'Cookie': '_gcl_au=1.1.522503471.1747379473; _wp_uid=1-885668873b114e1d96ce4a4767afbda2-s1740411294.586816|mac_osx|chrome-1cly2dn; CookieNo=2545041795; _ga_Y8D38WJBKH=GS2.3.s1747379494$o1$g1$t1747379589$j50$l0$h0; WMONID=giZoI1pl-77; RSCondition=[{"CookieIndex":"20250523193254","Cndt_No":0,"M_Id":"","Area_Code":"K000","Reg_Dt":"2025-05-23T19:32:54.7752732+09:00","IsKeep":true}]; ASP.NET_SessionId=rxuoxgrq4crrumayvvw3xbph; ECHO_SESSION=3791747999799602; _gcl_aw=GCL.1747999800.Cj0KCQjwucDBBhDxARIsANqFdr0nsrjn1TDJY9zrycjYMTDhM87sy0Ys-WQj6j5syeT_Rw4BhmAzQmYaAgVsEALw_wcB; _gcl_gs=2.1.k1$i1747999799$u166426661; _gac_UA-75522609-1=1.1747999801.Cj0KCQjwucDBBhDxARIsANqFdr0nsrjn1TDJY9zrycjYMTDhM87sy0Ys-WQj6j5syeT_Rw4BhmAzQmYaAgVsEALw_wcB; TR10148105490_t_uid=15175316018074103.1747999802241; TR10148105490_t_pa1=3.460.693.0.336d5ebc5436534e61d16e63ddfca327.2ca01310d0d2cb9dda2ba376cdb23028.null.0; DirectStat=ON; TR10148105490_t_pa2=3.460.693.0.336d5ebc5436534e61d16e63ddfca327.2ca01310d0d2cb9dda2ba376cdb23028.null.0; ASPSESSIONIDACDTADSR=MPCAAFAAPLLECKPHJNFLJLHP; ASPSESSIONIDCABTACSQ=JPMBPEAAGFGAEFJEDCEBJCDO; ASPSESSIONIDACTQASDT=NJBELGAAHMDOHGCJEONJKBEE; ASPSESSIONIDSSTTSQQT=NNALNLHBMBBIHOMCCCNBIFFD; KPIs=param=&keyword=; session=; sm=keyword=; GnbMeActvtNewAlert=N; GnbMeOpenNewAlert=Y; C%5FUSER=AAA=&UID=&DB%5FNAME=GG; User=UID=&Type=; ab.storage.deviceId.b9795c74-cdce-4881-a000-eb185c0d072e=%7B%22g%22%3A%225f33e322-cfc3-7f9d-da7d-c09520cb506a%22%2C%22c%22%3A1748248873217%2C%22l%22%3A1748248873229%7D; ab.storage.userId.b9795c74-cdce-4881-a000-eb185c0d072e=%7B%22g%22%3A%2247971485%22%2C%22c%22%3A1748248873228%2C%22l%22%3A1748248873229%7D; JK%5FUser=M%5FID=5eb292e0d1122da330a325c54496e563e0b75d2f3a3418d68ee03727b9beb1193c85b9b4e865dc796d5ef8fd44bf2941&Mem%5FName=ac71c7b064a423fb3c52dfa2b4d27283fd72667a9b51121b803c1c7fbdb6d43f0628bd532f7b0d119cc72471d1d5514d&Mem%5FName2=2caa13f2019645d471695181ae7f4917877e49290aaacf70cf4e13cd3ff37eb0d0b9275a5e8e12c5595ff1f56f79ab5c&LoginStat=e39674550c339785b598fcc0107e79df5f63e4fc442f247e853ed4db408497db&LoginTime=2025-05-26+18%3a10%3a00&DS%5FID=b0a685fc152f1adfae894a94e8f82e40&MemSysNo=47971485; ab.storage.sessionId.b9795c74-cdce-4881-a000-eb185c0d072e=%7B%22g%22%3A%2249a85d66-2c7c-4c8a-7d99-ac3051cd5200%22%2C%22e%22%3A1748252488317%2C%22c%22%3A1748248873228%2C%22l%22%3A1748250688317%7D; jobkorea=Site_Oem_Code=C1; GTMVars=b86daa8f8a80f8bb68260b0930f45617; MainRcntlyData=%3c%6c%69%3e%3c%61%20%68%72%65%66%3d%22%2f%72%65%63%72%75%69%74%2f%68%6f%6d%65%22%3e%c3%a4%bf%eb%c1%a4%ba%b8%3c%2f%61%3e%20%26%67%74%3b%20%3c%61%20%68%72%65%66%3d%22%2f%72%65%63%72%75%69%74%2f%6a%6f%62%6c%69%73%74%3f%6d%65%6e%75%63%6f%64%65%3d%6c%6f%63%61%6c%26%6c%6f%63%61%6c%6f%72%64%65%72%3d%31%22%20%63%6c%61%73%73%3d%22%63%61%74%65%22%3e%c1%f6%bf%aa%ba%b0%3c%2f%61%3e%3c%2f%6c%69%3e%7c%24%24%7c%3c%6c%69%3e%3c%61%20%68%72%65%66%3d%22%2f%72%65%63%72%75%69%74%2f%6a%6f%62%6c%69%73%74%3f%6d%65%6e%75%63%6f%64%65%3d%6c%6f%63%61%6c%26%6c%6f%63%61%6c%6f%72%64%65%72%3d%31%22%3e%c1%f6%bf%aa%ba%b0%3c%2f%61%3e%20%26%67%74%3b%20%3c%61%20%68%72%65%66%3d%22%2f%72%65%63%72%75%69%74%2f%6a%6f%62%6c%69%73%74%3f%6d%65%6e%75%63%6f%64%65%3d%6c%6f%63%61%6c%26%6c%6f%63%61%6c%3d%4b%30%34%30%22%20%63%6c%61%73%73%3d%22%63%61%74%65%22%3e%c0%ce%c3%b5%20%3c%2f%61%3e%3c%2f%6c%69%3e%20%26%67%74%3b%20%3c%61%20%68%72%65%66%3d%22%2f%72%65%63%72%75%69%74%2f%6a%6f%62%6c%69%73%74%3f%6d%65%6e%75%63%6f%64%65%3d%6c%6f%63%61%6c%26%6c%6f%63%61%6c%3d%4b%30%34%30%22%20%63%6c%61%73%73%3d%22%63%61%74%65%22%3e%c0%ce%c3%b5%20%b3%b2%b5%bf%b1%b8%3c%2f%61%3e%3c%2f%6c%69%3e%7c%24%24%7c; _gid=GA1.3.724363236.1748337539; TR10148105490_t_if=15.0.0.0.null.null.null.15175096617570166; sm=keyword=%eb%83%89%eb%8f%99; _ga_GQWHSF87P4=GS2.1.s1748337537$o9$g1$t1748337624$j59$l0$h0$de7Q0wL5ZymN8TphTrsFjnJ0GcyHpYhyvyA; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22a5DMRDEV3WAQvmPQ4PfP%22%2C%22expiryDate%22%3A%222026-05-27T09%3A20%3A24.094Z%22%7D; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%222069996167.1747379473%22%2C%22expiryDate%22%3A%222026-05-27T09%3A20%3A24.098Z%22%7D; _ga=GA1.3.2069996167.1747379473; _gat_trackerOne2=1; cto_bundle=nNU7SV9BbjJHaGc4NFhwWU9SVSUyRnV5WGlxc2IzOG9tVHhuTGx0dWo1aUxVciUyRnIyUnZSMnhxcFJ3MkhSZFJ4YUNCdVhHckpPRm1mYXJVOWVtN2NtaFExVEIlMkZPNzk2b09XQTVPUWM5OHZRWW5GbjlmTmYxN3hlM0Q0UUpjVjZNZmYxRjdmMTk4QUhkSCUyRm5WdlNiSzVRQnQ3QjJ3c1plU2VPOFdWN1A4aVcyUjlUR2o0WldrMjZFcWJ2NFpBRGRYOXk2ZmlQQ3FVZ0hLaXBnOTFacE1uZ3M1QU51VzBwZXZEaWh6QmcxMkppRzJTb3pLR05RRUR1SEJaSWZDd3RJdlJ3WWZiVFV2VjhSQU1JaFFQdDZhYjBOaDlieSUyRml2cUc2bUtaMzFiVGpTM24wVVZjOE5KMmQ3cUtGbVVZRFZ5SG9OWEVuWTMyVEhvS2p3U0Z6anIzd0h5Y0lmY2MlMkJJOENZNVJ4WHNkJTJCOWR4RHFEN3BUZyUzRA; _ga_H72LM07GXG=GS2.3.s1748337539$o7$g1$t1748337624$j60$l0$h0$dh3ozKro5gBPPd9CJhOuQ0Vn2M00SgKkrAg; TR10148105490_t_sst=15175250691812166.1748337624322; GTMVarsFrom=NET:18:20:28',
            }

            params = {
                'stext': a,
                'tabType': 'recruit',
                'Page_No': str(idx),
            }

            response = requests.get(
                'https://www.jobkorea.co.kr/Search/TotalSearchRecruitList',
                params=params,
                headers=headers,
            )
            if response.status_code==200:
                html=response.text
                soup=BeautifulSoup(html,'html.parser')
                urls=soup.find_all(class_="information-title-link")

                for i in urls:
                    exact_url=i["href"]
                    recruit_url_list.append(exact_url)
                    # print(exact_url)
                print(recruit_url_list)
            else:
                break

        df=sub_crawl(df,driver,recruit_url_list)
        export_to_excel(df)
        
    elif a==2:
        print("지역을 선택해주세요. 선택 숫자를 누르고 엔터를 눌러주세요.")
        a=input()
        recruit_url_list = []
        dict={"서울":"I000", "경기":"B000"}

        while True:
            if idx==t:
                break
            time.sleep(0.5)
            idx+=1
            headers = {
                'Accept': 'text/html, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.9,ko;q=0.8,ja;q=0.7',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://www.jobkorea.co.kr',
                'Referer': 'https://www.jobkorea.co.kr/recruit/joblist?menucode=local&localorder=1',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest',
                'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                # 'Cookie': '_gcl_au=1.1.522503471.1747379473; _wp_uid=1-885668873b114e1d96ce4a4767afbda2-s1740411294.586816|mac_osx|chrome-1cly2dn; CookieNo=2545041795; _ga_Y8D38WJBKH=GS2.3.s1747379494$o1$g1$t1747379589$j50$l0$h0; MainRcntlyData=%3c%6c%69%3e%3c%61%20%68%72%65%66%3d%22%2f%72%65%63%72%75%69%74%2f%68%6f%6d%65%22%3e%c3%a4%bf%eb%c1%a4%ba%b8%3c%2f%61%3e%20%26%67%74%3b%20%3c%61%20%68%72%65%66%3d%22%2f%72%65%63%72%75%69%74%2f%6a%6f%62%6c%69%73%74%3f%6d%65%6e%75%63%6f%64%65%3d%6c%6f%63%61%6c%26%6c%6f%63%61%6c%6f%72%64%65%72%3d%31%22%20%63%6c%61%73%73%3d%22%63%61%74%65%22%3e%c1%f6%bf%aa%ba%b0%3c%2f%61%3e%3c%2f%6c%69%3e%7c%24%24%7c; ASP.NET_SessionId=yq0sfvdow12fukcnutjqe4dk; jobkorea=Site_Oem_Code=C1; ECHO_SESSION=9151747995666836; GTMVars=b86daa8f8a80f8bb68260b0930f45617; _gcl_gs=2.1.k1$i1747995666$u166426661; Main_Top_Banner_Seq=1; TR10148105490_t_uid=15175316018414051.1747995671991; TR10148105490_t_if=3.460.693.0.336d5ebc5436534e61d16e63ddfca327.9ed926522244c49cefc405b26aa21d21.null.0; TR10148105490_t_pa1=3.460.693.0.336d5ebc5436534e61d16e63ddfca327.9ed926522244c49cefc405b26aa21d21.null.0; _gid=GA1.3.81252912.1747995672; TR10148105490_t_pa2=3.460.693.0.336d5ebc5436534e61d16e63ddfca327.9ed926522244c49cefc405b26aa21d21.null.0; _gac_UA-75522609-1=1.1747996148.Cj0KCQjwucDBBhDxARIsANqFdr07JiSbcZVLBsrbRJWr6Uo7e27U5rJf2xJYdqBJzWdrLtCjTRh8EdIaAqJ5EALw_wcB; WMONID=giZoI1pl-77; _gat_trackerOne2=1; RSCondition=[{"CookieIndex":"20250523193221","Cndt_No":0,"M_Id":"","Area_Code":"K000","Reg_Dt":"2025-05-23T19:32:21.8020969+09:00","IsKeep":true}]; _gcl_aw=GCL.1747996349.Cj0KCQjwucDBBhDxARIsANqFdr07JiSbcZVLBsrbRJWr6Uo7e27U5rJf2xJYdqBJzWdrLtCjTRh8EdIaAqJ5EALw_wcB; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%222069996167.1747379473%22%2C%22expiryDate%22%3A%222026-05-23T10%3A32%3A28.982Z%22%7D; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22a5DMRDEV3WAQvmPQ4PfP%22%2C%22expiryDate%22%3A%222026-05-23T10%3A32%3A28.982Z%22%7D; _ga=GA1.3.2069996167.1747379473; cto_bundle=HxnSyl9BbjJHaGc4NFhwWU9SVSUyRnV5WGlxc1p2cG5yejEwSUZXTXE5WGslMkZmcFJWNFVTTzlFWDVDODdjb3djWlJkZyUyRlI3RG5PZkxla3l3eFNJSSUyRlUyZFZWZEdiSDluVzU2ayUyRnRlS2ZtRFFJUDglMkZYRDhOd3BDSThrVjZielpoRWh2SXElMkY1dG9GWncwaTNxMzlqakN6aEhxUk0lMkJJeVFLJTJGcWo2RTRvTmg1Nzh4UkxRdTBHdlpLeXZKd2w1b0lpNEUwM1pPY2lXU1hYJTJCMyUyQjRkbWY4Nm1tSXJWOFBFTmp6R3laQVdwWXZubFRUM0R0bEVIaVhKSzhoa0t5b3lLTm1KRG9rdXl3cGljVnFHdHk3TkF3TUFVd1RpeEo0WTA2TyUyRkFFSXh5JTJGYmg1M1FxMEJHY1RLVlRmWG1QdVF0ak5HeFdWVlIlMkZ1Zmc; _ga_H72LM07GXG=GS2.3.s1747995672$o3$g1$t1747996349$j41$l0$h0$dh3ozKro5gBPPd9CJhOuQ0Vn2M00SgKkrAg; TR10148105490_t_sst=15175994400001414.1747996349546; _ga_GQWHSF87P4=GS2.1.s1747995670$o5$g1$t1747996369$j4$l0$h0$de7Q0wL5ZymN8TphTrsFjnJ0GcyHpYhyvyA; GTMVarsFrom=NET:19:32:50',
            }

            data = {
                'isDefault': 'true',
                'condition[local]': 'K000',
                'condition[menucode]': '',
                'page': str(idx),
                'direct': '0',
                'order': '20',
                'pagesize': '40',
                'tabindex': '0',
                'onePick': '0',
                'confirm': '0',
                'profile': '0',
            }

            response = requests.post('https://www.jobkorea.co.kr/Recruit/Home/_GI_List/', headers=headers, data=data)
            if response.status_code==200:
                html=response.text
                soup=BeautifulSoup(html,'html.parser')
                urls=soup.find_all(class_="titBx")

                for i in urls:
                    exact_url=i.find("a")["href"]
                    recruit_url_list.append(exact_url)
                    # print(exact_url)
            else:
                break
        df=sub_crawl(df,driver,recruit_url_list)
        
        export_to_excel(df)


if __name__ == '__main__':
    crawl_jobkorea()