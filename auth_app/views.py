from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django_filters import exceptions
from rest_framework import generics, response, status, exceptions, viewsets
from .models import CustomUser as User, UserProfile, Notifications, UserPublication, Tag, Comment, AnonymousUser
from .serializers import (RegUserSerializer, LoginSerializer,
                          UserProfileSerializer, NotificationSerializer, UserPublicationSerializer, CommentSerializer)
from rest_framework.permissions import AllowAny
from .permissions import UserProfilePermission, NotificationPermission
from rest_framework.decorators import action
from haka_app import serializers as haka_sz, models as haka_md
from rest_framework.views import APIView
from .utils import get_client_ip
from django.http import Http404, HttpResponseBadRequest
from random import shuffle, choice, randint
import requests
usernames = ['atuny0', 'hbingley1', 'rshawe2', 'yraigatt3', 'kmeus4', 'jtreleven5', 'dpettegre6', 'ggude7', 'nloiterton8', 'umcgourty9', 'acharlota', 'rhallawellb', 'lgribbinc', 'mturleyd', 'kminchelle', 'dpierrof', 'vcholdcroftg', 'sberminghamh', 'bleveragei', 'aeatockj', 'ckensleyk', 'froachel', 'beykelhofm', 'brickeardn', 'dfundello', 'lgronaverp', 'fokillq', 'xisherwoodr', 'jissetts', 'kdulyt', 'smargiottau', 'lskeelv', 'gsilcockw', 'aaughtonx', 'mbrooksbanky', 'dalmondz', 'nwytchard10', 'igannan11', 'lgherardi12', 'lgutridge13', 'cslateford14', 'mhaslegrave15', 'kbrecknock16', 'rlaxe17', 'pidill18', 'rmcritchie19', 'rlangston1a', 'jevanson1b', 'ssarjant1c', 'xlinster1d', 'tmullender1e', 'gmein1f', 'gmaccumeskey1g', 'bpetts1h', 'ajozef1i', 'oyakushkev1j', 'bpickering1k', 'nworley1l', 'klife1m', 'dlambarth1n', 'cepgrave1o', 'mpoyner1p', 'eburras1q', 'gfernandes1r', 'hollet1s', 'hfasey1t', 'gbarhams1u', 'rstrettle1v', 'btegler1w', 'cmasurel1x', 'omarsland1y', 'mcrumpe1z', 'wfeldon20', 'ahinckes21', 'ptilson22', 'cgaber23', 'rkingswood24', 'dbuist25', 'pmoraleda26', 'vkohrt27', 'capplewhite28', 'kogilvy29', 'gconford2a', 'dmantle2b', 'kpondjones2c', 'whuman2d', 'fschlagman2e', 'agreenhouse2f', 'cdwyr2g', 'omottley2h', 'hyaknov2i', 'clambol2j', 'dduggan2k', 'jtossell2l', 'cchomiszewski2m', 'bgoby2n', 'cdavydochkin2o', 'zstenning2p', 'flesslie2q', 'pcumbes2r']
passwords = ['9uQFF1Lh', 'CQutx25i8r', 'OWsTbMUgFc', 'sRQxjPfdS', 'aUTdmmmbH', 'zY1nE46Zm', 'YVmhktgYVS', 'MWwlaeWcOoF6', 'HTQxxXV9Bq4', 'i0xzpX', 'M9lbMdydMN', 'esTkitT1r', 'ftGj8LZTtv9g', 'GyLnCB8gNIp', '0lelplR', 'Vru55Y4tufI4', 'mSPzYZfR', 'cAjfb8vg', 'UZGAiqPqWQHQ', 'szWAG6hc', 'tq7kPXyf', 'rfVSKImC', 'zQwaHTHbuZyr', 'bMQnPttV', 'k9zgV68UKw8m', '4a1dAKDv9KB9', 'xZnWSWnqH', 'HLDqN5vCF', 'ePawWgrnZR8L', '5t6q4KC7O', 'pSGvhgS2A', 'Eolj9Svg28', 'AI6RmBSXjw2S', 'Vzwc72RhNGu', '9V8lqrkq', 'wM5tOHRMQt6g', 'ij8mFevk', 'MB63jkg3W', 'm0eNOs', 'SqR03CE', 'wpbWfIbpIgGc', 'sq5FYgvU', 'KoNiIBiHE', 'OHFibd', 'GbBDdjbKG1a2', 'QFSwkjeVEhOQ', 'rU8ybew', '1Dlvqluwi5zO', 'y2YBSxtcmXVW', 'WHAE1AtmDh', 'fxJRvUVCFA95', 'VYaG1Ew', 'bETj6uCOI', 'IxI5sjpNT5F', 'uAVFvWB0Pxi', 'UB3BAOn8Sj7', 'J4f0Es7sxXVO', 'HhWAr5TR', 'ZdEndJIQLM', '1zosSj9eR', 'BnC5P3MdJ', 'nCTH1QhLCNY', 'Y7UmdaATt', 'LzI2Plmj', 'WK46QB', 'vDMcOSFj0', 'uDO326b3Hn7O', 'ryhdXB', 'xx9O9fzZI', 'es8eVhVy4c', 'MT463NsEI', 'F8JxU31tNw', 'cLcJUmA', 'dIoZ2huN', 'jNbmsr', 'nieEPfUI', '0VNksmUL7', 'OlP0CIw', 'QrZGjkTF8eX', 'yMmUuTZDdPC', 'oqqDPsff', 'aGX6R9Xd9bd2', 'CNZ3xN', 'SBnr789', 'H4IiV9f8jb', 'JyHAUcC', 'icEdQz4YnwV', 'VmqqWniF', 'x96XD8Fm', '67oJrJe6ta', 'Xw8nIye1', 'MJRFJutRGS', 'Hf0TgLPXG', 'LTRc4mC', 'xjuQsRDR0NP6', 'aKzuEqfI3wU', 'N1node', 'Ck5jBaO6691g', 'XUKU613LscMS', 'obhSsvCF8c0']
emails = ['atuny0@sohu.com', 'hbingley1@plala.or.jp', 'rshawe2@51.la', 'yraigatt3@nature.com', 'kmeus4@upenn.edu', 'jtreleven5@nhs.uk', 'dpettegre6@columbia.edu', 'ggude7@chron.com', 'nloiterton8@aol.com', 'umcgourty9@jalbum.net', 'acharlota@liveinternet.ru', 'rhallawellb@dropbox.com', 'lgribbinc@posterous.com', 'mturleyd@tumblr.com', 'kminchelle@qq.com', 'dpierrof@vimeo.com', 'vcholdcroftg@ucoz.com', 'sberminghamh@chron.com', 'bleveragei@so-net.ne.jp', 'aeatockj@psu.edu', 'ckensleyk@pen.io', 'froachel@howstuffworks.com', 'beykelhofm@wikispaces.com', 'brickeardn@fema.gov', 'dfundello@amazon.co.jp', 'lgronaverp@cornell.edu', 'fokillq@amazon.co.jp', 'xisherwoodr@ask.com', 'jissetts@hostgator.com', 'kdulyt@umich.edu', 'smargiottau@altervista.org', 'lskeelv@webeden.co.uk', 'gsilcockw@infoseek.co.jp', 'aaughtonx@businessweek.com', 'mbrooksbanky@gnu.org', 'dalmondz@joomla.org', 'nwytchard10@blogspot.com', 'igannan11@microsoft.com', 'lgherardi12@washington.edu', 'lgutridge13@sun.com', 'cslateford14@blogspot.com', 'mhaslegrave15@springer.com', 'kbrecknock16@marriott.com', 'rlaxe17@tamu.edu', 'pidill18@china.com.cn', 'rmcritchie19@topsy.com', 'rlangston1a@51.la', 'jevanson1b@admin.ch', 'ssarjant1c@statcounter.com', 'xlinster1d@bravesites.com', 'tmullender1e@scientificamerican.com', 'gmein1f@nasa.gov', 'gmaccumeskey1g@buzzfeed.com', 'bpetts1h@smugmug.com', 'ajozef1i@usatoday.com', 'oyakushkev1j@oracle.com', 'bpickering1k@clickbank.net', 'nworley1l@thetimes.co.uk', 'klife1m@i2i.jp', 'dlambarth1n@blinklist.com', 'cepgrave1o@biblegateway.com', 'mpoyner1p@google.co.uk', 'eburras1q@go.com', 'gfernandes1r@virginia.edu', 'hollet1s@trellian.com', 'hfasey1t@home.pl', 'gbarhams1u@cnet.com', 'rstrettle1v@globo.com', 'btegler1w@elegantthemes.com', 'cmasurel1x@baidu.com', 'omarsland1y@washingtonpost.com', 'mcrumpe1z@techcrunch.com', 'wfeldon20@netlog.com', 'ahinckes21@google.es', 'ptilson22@360.cn', 'cgaber23@prlog.org', 'rkingswood24@usa.gov', 'dbuist25@hao123.com', 'pmoraleda26@symantec.com', 'vkohrt27@hostgator.com', 'capplewhite28@nationalgeographic.com', 'kogilvy29@blogtalkradio.com', 'gconford2a@wordpress.com', 'dmantle2b@reuters.com', 'kpondjones2c@nsw.gov.au', 'whuman2d@hp.com', 'fschlagman2e@deliciousdays.com', 'agreenhouse2f@mashable.com', 'cdwyr2g@shop-pro.jp', 'omottley2h@hugedomains.com', 'hyaknov2i@hhs.gov', 'clambol2j@bloglovin.com', 'dduggan2k@simplemachines.org', 'jtossell2l@drupal.org', 'cchomiszewski2m@cbsnews.com', 'bgoby2n@washingtonpost.com', 'cdavydochkin2o@globo.com', 'zstenning2p@list-manage.com', 'flesslie2q@google.nl', 'pcumbes2r@networkadvertising.org']

firstnames = ['Terry', 'Sheldon', 'Terrill', 'Miles', 'Mavis', 'Alison', 'Oleta', 'Ewell', 'Demetrius', 'Eleanora', 'Marcel', 'Assunta', 'Trace', 'Enoch', 'Jeanne', 'Trycia', 'Bradford', 'Arely', 'Gust', 'Lenna', 'Doyle', 'Tressa', 'Felicity', 'Jocelyn', 'Edwina', 'Griffin', 'Piper', 'Kody', 'Macy', 'Maurine', 'Luciano', 'Kaya', 'Lee', 'Darien', 'Jacklyn', 'Angelica', 'Delfina', 'Thaddeus', 'Salvatore', 'Jasmin', 'Nicklaus', 'Tiara', 'Garret', 'Reginald', 'Humberto', 'Justus', 'Coralie', 'Felicita', 'Pearl', 'Johnathon', 'Jerry', 'Elbert', 'Sincere', 'Telly', 'Hal', 'Megane', 'Toy', 'Deanna', 'Marcella', 'Rachel', 'Nora', 'Mozell', 'Nasir', 'Quinn', 'Jeanne', 'Terrence', 'Davonte', 'Everette', 'Oda', 'Twila', 'Amelia', 'Frederique', 'Clotilde', 'Moriah', 'Claudia', 'Deon', 'Amos', 'Frankie', 'Harrison', 'Guy', 'Sidney', 'Maymie', 'Rita', 'Aniya', 'Angelica', 'Rupert', 'Eleazar', 'Anais', 'Gayle', 'Wilma', 'Arne', 'Emely', 'Fabiola', 'Kari', 'Rory', 'Cristobal', 'Allene', 'Lempi', 'Terrell', 'Tevin']
descriptions = ['Capitol University', 'Stavropol State Technical University', 'University of Cagayan Valley', 'Shenyang Pharmaceutical University', 'Estonian University of Life Sciences', 'Universidade da Beira Interior', 'Institut Sains dan Teknologi Al Kamal', 'Wenzhou Medical College', 'Nanjing University of Economics', 'Melaka City Polytechnic', 'Hodeidah University', 'Kiev Slavonic University', 'Dallas Christian College', 'University of Sri Jayawardenapura', 'Donghua University, Shanghai', 'Technical University of Mining and Metallurgy Ostrava', 'Technical University of Mining and Metallurgy Ostrava', 'Universidade Estadual do Ceará', 'Xinjiang University', 'Moraine Valley Community College', 'Nanjing University of Traditional Chinese Medicine', 'Universitat Rámon Llull', 'University of lloilo', 'Bashkir State Medical University', 'Wuhan University of Technology', 'Universitas Bojonegoro', 'Sultanah Bahiyah Polytechnic', 'Science University of Tokyo', "Fuji Women's College", 'Poznan School of Banking', 'Mendel University of Agriculture and Forestry', 'Goucher College', 'Yonok University', 'Université Paris Nanterre (Paris X)', 'University of Perpetual Help, System Dalta', 'Universitas Trilogi', 'Ho Chi Minh City University of Transport', 'Universitas Mataram', 'Södertörn University College', 'Okinawa Prefectural University of Fine Arts', 'Institut Teknologi Sepuluh Nopember', 'Universidade Aberta Lisboa', 'Harbin Engineering University', 'Cevro Institut College', 'Université de Lomé', 'Escuela Agricola Panamericana Zamorano', 'International University Institute of Luxembourg', 'Jiangxi Agricultural University', 'Université de Fianarantsoa', 'Instituto Politécnico de Coimbra', "Queen's University", 'Hainan University', 'Politeknik Negeri Jakarta', 'Universitas Wisnuwardhana', 'Academy of Humanities and Economics in Lodz', 'Texas Lutheran University', 'Judson College Marion', 'Azerbaijan Medical University', 'Universitas Proklamasi 45', 'Mendel University of Agriculture and Forestry', 'California Coast University', 'Capital University of Medical Sciences', 'Universitas Nasional Jakarta', 'University of the Gambia', 'Universitas Jember', 'Notre Dame University', 'Universidad de La Salle, Bajío', 'Centro Universitário Adventista de São Paulo', 'Universidade Federal de Ouro Preto', 'Wuhan Automobile Polytechnical University', 'Universitas Komputer Indonesia', 'San Beda College', 'Sichuan Normal University', 'University of Ljubljana', 'Huaihua Medical College', 'University of Western Macedonia', 'University of Mauritius', 'Institut des Sciences de la Matière et du Rayonnement', 'Universitas Diponegoro', 'Dongbei University of Finance And Economics', 'Universitas Darma Persada', 'University Centre of the Westfjords', 'Yantai Education Institute & Yantai Television University', 'University of Eastern Philippines', 'University of Bergen', 'Instituto Tecnológico de Santo Domingo', 'Universidad Cooperativa de Colombia', 'Islamic Azad University, Janah', "Université d'Etat d'Haiti", 'Altai State Technical University', 'Károl Gáspár University of the Reformed Church', 'Tianjin University of Technology', 'Chongqing Telecommunication College', 'PTPL College', 'Politeknik Negeri Lhokseumawe', 'Luhansk Taras Shevchenko National Pedagogical University', 'St.Cyril and Methodius University', 'Fukushima Medical College', 'Liepaja Pedagogical Higher School', 'Gotland University College']
images = ['https://robohash.org/hicveldicta.png', 'https://robohash.org/doloremquesintcorrupti.png', 'https://robohash.org/consequunturautconsequatur.png', 'https://robohash.org/facilisdignissimosdolore.png', 'https://robohash.org/adverovelit.png', 'https://robohash.org/laboriosamfacilisrem.png', 'https://robohash.org/cupiditatererumquos.png', 'https://robohash.org/quiaharumsapiente.png', 'https://robohash.org/excepturiiuremolestiae.png', 'https://robohash.org/aliquamcumqueiure.png', 'https://robohash.org/impeditautest.png', 'https://robohash.org/namquaerataut.png', 'https://robohash.org/voluptatemsintnulla.png', 'https://robohash.org/quisequienim.png', 'https://robohash.org/autquiaut.png', 'https://robohash.org/porronumquamid.png', 'https://robohash.org/accusantiumvoluptateseos.png', 'https://robohash.org/nihilharumqui.png', 'https://robohash.org/delenitipraesentiumvoluptatum.png', 'https://robohash.org/ipsumutofficiis.png', 'https://robohash.org/providenttemporadelectus.png', 'https://robohash.org/temporarecusandaeest.png', 'https://robohash.org/odioquivero.png', 'https://robohash.org/odiomolestiaealias.png', 'https://robohash.org/doloremautdolores.png', 'https://robohash.org/laboriosammollitiaut.png', 'https://robohash.org/nequeodiosapiente.png', 'https://robohash.org/consequunturabnon.png', 'https://robohash.org/amettemporeea.png', 'https://robohash.org/perferendisideveniet.png', 'https://robohash.org/rerumfugiatamet.png', 'https://robohash.org/etquiquibusdam.png', 'https://robohash.org/providentdoloremarchitecto.png', 'https://robohash.org/utnonnobis.png', 'https://robohash.org/nequeexercitationemanimi.png', 'https://robohash.org/vitaenonqui.png', 'https://robohash.org/officiisprovidentlaborum.png', 'https://robohash.org/veritatisperspiciatisqui.png', 'https://robohash.org/quosautquia.png', 'https://robohash.org/voluptatesolutaconsequuntur.png', 'https://robohash.org/quiaconsecteturaut.png', 'https://robohash.org/perferendisestanimi.png', 'https://robohash.org/amaioresqui.png', 'https://robohash.org/vitaeharumquia.png', 'https://robohash.org/liberoquaeratquidem.png', 'https://robohash.org/veritatismodiest.png', 'https://robohash.org/quivoluptatepraesentium.png', 'https://robohash.org/numquamcumquereiciendis.png', 'https://robohash.org/etnemoet.png', 'https://robohash.org/nisietqui.png', 'https://robohash.org/aliquideosquidem.png', 'https://robohash.org/omnisipsasit.png', 'https://robohash.org/minimaquamcorrupti.png', 'https://robohash.org/quianonquia.png', 'https://robohash.org/animiautillo.png', 'https://robohash.org/voluptatemexplicaboasperiores.png', 'https://robohash.org/eumestdolor.png', 'https://robohash.org/porroaccusamuseveniet.png', 'https://robohash.org/eaipsaaliquam.png', 'https://robohash.org/doloremtemporamolestiae.png', 'https://robohash.org/corporisvoluptatumdicta.png', 'https://robohash.org/sintsequitenetur.png', 'https://robohash.org/dignissimosplaceatet.png', 'https://robohash.org/distinctioullamsaepe.png', 'https://robohash.org/reprehenderitquisanimi.png', 'https://robohash.org/facilisomnisvoluptatem.png', 'https://robohash.org/ipsadistinctiovero.png', 'https://robohash.org/cumquesedrem.png', 'https://robohash.org/asperioressolutaet.png', 'https://robohash.org/quiaeaquefacere.png', 'https://robohash.org/voluptassimiliqueet.png', 'https://robohash.org/doloremqueatqueet.png', 'https://robohash.org/estipsamincidunt.png', 'https://robohash.org/voluptatemdolorumvel.png', 'https://robohash.org/idvoluptatemrepellendus.png', 'https://robohash.org/authicnon.png', 'https://robohash.org/quasialiquidrerum.png', 'https://robohash.org/voluptaseligendiaut.png', 'https://robohash.org/hicadipisciodio.png', 'https://robohash.org/quaeratpariaturet.png', 'https://robohash.org/dolorumdelenitinon.png', 'https://robohash.org/providentquiaaut.png', 'https://robohash.org/sapientelaborumminima.png', 'https://robohash.org/aliasiurenam.png', 'https://robohash.org/atetsit.png', 'https://robohash.org/mollitiasimiliqueneque.png', 'https://robohash.org/facerealiquidexercitationem.png', 'https://robohash.org/laborumvoluptatibusnulla.png', 'https://robohash.org/inventoredelenitiquas.png', 'https://robohash.org/minimadoloreslaborum.png', 'https://robohash.org/necessitatibusvoluptatemvero.png', 'https://robohash.org/cumqueharumsunt.png', 'https://robohash.org/undeutveritatis.png', 'https://robohash.org/quisquamhicin.png', 'https://robohash.org/autcommodivoluptas.png', 'https://robohash.org/deseruntfaciliset.png', 'https://robohash.org/adipiscisiteius.png', 'https://robohash.org/estetlaudantium.png', 'https://robohash.org/maioresethic.png', 'https://robohash.org/eosvoluptasquia.png']




class RegUserViewSet(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegUserSerializer
    permission_classes = [AllowAny]     # Исключение Auth


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]     # Исключение auth

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,   # Сериализируем данные юзера
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = authenticate(username=serializer.validated_data['username'],
                            password=serializer.validated_data['password'])

        if not user:
            raise exceptions.AuthenticationFailed()
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        token, _ = Token.objects.get_or_create(user=user)

        return response.Response(data={"token": token.key},
                                 status=status.HTTP_200_OK)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [UserProfilePermission]

    @action(detail=True, methods=['POST'], url_path='subscribe')
    def follow(self, request, pk):
        target_user_profile = UserProfile.objects.get(id=pk)
        current_user_profile = UserProfile.objects.get(user=request.user)


        current_user_profile.following.add(target_user_profile.user)
        target_user_profile.followers.add(current_user_profile.user)

        current_user_profile.save()
        target_user_profile.save()
        return response.Response({"detail": "You subscribed"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path='unsubscribe')
    def unfollow(self, request, pk):
        target_user_profile = UserProfile.objects.get(id=pk)
        current_user_profile = UserProfile.objects.get(user=request.user)

        current_user_profile.following.remove(target_user_profile.user)
        target_user_profile.followers.remove(current_user_profile.user)

        current_user_profile.save()
        target_user_profile.save()
        return response.Response({"detail": "You unsubscribed"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='followers')
    def get_followers(self, request, pk):
        user_profile = UserProfile.objects.get(id=pk)
        followers = user_profile.followers.all()
        return response.Response(RegUserSerializer(followers, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='following')
    def get_following(self, request, pk):
        user_profile = UserProfile.objects.get(id=pk)
        following = user_profile.following.all()
        return response.Response(RegUserSerializer(following, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='visited-events')
    def get_visited_events(self, request, pk):
        user_profile = UserProfile.objects.get(id=pk)
        visited_events = user_profile.visited_events.all()
        return response.Response(haka_sz.EventSerializer(visited_events, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='future-events')
    def get_future_events(self, request, pk):
        user_profile = UserProfile.objects.get(id=pk)
        future_events = user_profile.future_events.all()
        print(future_events)
        return response.Response(haka_sz.EventSerializer(future_events, many=True).data, status=status.HTTP_200_OK)

    # @action(detail=True, methods=['GET'], url_path='events')
    # def get_events(self, request, pk):
    #     user_profile = UserProfile.objects.get(id=pk)
    #     events = haka_md.Event.objects.filter(user=user_profile.user)
    #     return response.Response(haka_sz.EventSerializer(events, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='friends')
    def get_friends(self, request, pk):
        user_profile = self.get_object()
        friend_profiles = UserProfile.objects.filter(followers=user_profile.user)

        friends_list = []
        for friend_profile in friend_profiles:
            if user_profile.user in friend_profile.following.all():
                friends_list.append({
                    'user_id': friend_profile.user.id,
                    'username': friend_profile.user.username,
                })

        return response.Response(friends_list, status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='public')
    def get_userprofile_publications(self, request, pk):
        public = UserPublication.objects.filter(user_profile_id=pk)
        return response.Response(UserPublicationSerializer(public, many=True).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='generate-users')
    def generate_publications_dummyjson(self, request):
        for i in range(98):
            print(i)
            user, created = User.objects.get_or_create(username=usernames[i], email=emails[i], password=passwords[i])
            user.save()
            userprofile, created = UserProfile.objects.get_or_create(user=user)
            userprofile.name = firstnames[i]
            userprofile.description = descriptions[i]
            userprofile.img = images[i]

            userprofile.save()
        return response.Response(UserPublicationSerializer(userprofile).data, status=status.HTTP_200_OK)




class NotificationViewSet(APIView):
    queryset = Notifications.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [NotificationPermission]

    def get(self, request):
        if self.request.user.is_authenticated:
            user = self.request.user
            notifications = Notifications.objects.filter(user=user)
            return response.Response(NotificationSerializer(notifications, many=True).data, status=status.HTTP_200_OK)
        else:
            return response.Response(NotificationSerializer(Notifications.objects.none()).data, status=status.HTTP_404_NOT_FOUND)


class UserPublicationView(viewsets.ModelViewSet):
    serializer_class = UserPublicationSerializer
    permission_classes = [AllowAny]
    queryset = UserPublication.objects.all()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            userprofile = UserProfile.objects.get(user=self.request.user)
            if userprofile:
                serializer.save(user_profile=userprofile)

    def create(self, request, *args, **kwargs):
        tags = request.data.get('tags')
        if tags:
            tags_list = []
            for i in request.data['tags']:
                tag, created = Tag.objects.get_or_create(hashtag=i)
                tags_list.append(tag.id)
            request.data['tags'] = tags_list
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        publication_pk = self.kwargs.get('public_pk')
        try:
            publication = UserPublication.objects.get(id=publication_pk)
            comments = Comment.objects.filter(publication=publication)
            return comments
        except UserPublication.DoesNotExist:
            raise Http404("UserPublication matching query does not exist")

    def create(self, request, *args, **kwargs):
        publication_pk = self.kwargs.get('public_pk')
        if publication_pk:
            publication = UserPublication.objects.get(id=publication_pk)
            content = request.data.get('content')
            if content:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                if self.request.user.is_authenticated:
                    user = self.request.user
                    serializer.save(user=user, content=content, publication=publication)
                    headers = self.get_success_headers(serializer.data)
                    return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
                ip_address = get_client_ip(self.request)
                session_key = self.request.session.session_key
                if session_key:
                    anonymous, created = AnonymousUser.objects.get_or_create(ip_address=ip_address)
                    anonymous.session_key = session_key
                    serializer.save(anonymous=anonymous, content=content, publication=publication)
                    headers = self.get_success_headers(serializer.data)
                    return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
                return response.Response({"detail": "Нет сессии, вероятно вы подключены не через браузер"},
                                         status=status.HTTP_400_BAD_REQUEST)
            return response.Response({"detail": "Напишите content"}, status=status.HTTP_400_BAD_REQUEST)
        return response.Response({"detail": "Неверный айди публикации"}, status=status.HTTP_404_NOT_FOUND)


class TagViewSet(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        search_tags = request.GET.get('search', '')
        if not search_tags:
            return response.Response({"detail": "Параметр 'search' должен содержать хэштеги через запятую."},
                                     status=status.HTTP_400_BAD_REQUEST)

        search_tags_list = search_tags.split(',')

        events = haka_md.Event.objects.filter(display_to_all=True, tags__hashtag__in=search_tags_list)
        user_publications = UserPublication.objects.filter(tags__hashtag__in=search_tags_list)

        serialized_events = haka_sz.EventSerializer(events, many=True).data
        serialized_user_publications = UserPublicationSerializer(user_publications, many=True).data

        combined_list = serialized_events + serialized_user_publications
        shuffle(combined_list)

        return response.Response(combined_list)











